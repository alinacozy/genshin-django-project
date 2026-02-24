from django.shortcuts import render, redirect, get_object_or_404
from .models import Character, UserCharacter, UserInventory, PlannedCharacter
from .forms import CharacterForm, UserCharacterForm, PlannedCharacterForm, ExPlannedCharacterForm
from django.views.generic import UpdateView
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import ensure_csrf_cookie

import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from .services.materials_aggregator import MaterialsAggregator
from .services.materials_calculator import MaterialsCalculator


def characters_home(request):
    characters=Character.objects.all()
    return render(request, 'characters/home.html', {'characters': characters})

class CharacterUpdateView(UpdateView):
    model = Character
    template_name = 'characters/create.html'
    form_class = CharacterForm

@login_required
def create(request):
    error=''
    if request.method == "POST":
        form = CharacterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/characters')
        else:
            error=form.errors

    form=CharacterForm()
    data={
        'form':form,
        'error':error
    }
    return render(request, 'characters/create.html', data)

@login_required
def calculate(request):
    only_obtained = request.GET.get('only_obtained') == '1'

    characters = UserCharacter.objects.filter(user=request.user)
    calculator = MaterialsCalculator()
    materials = calculator.calculate_all(characters, only_obtained=only_obtained)
    aggregated = MaterialsAggregator().aggregate_materials(materials, request_user=request.user)
    data = {
        'aggregated': aggregated,
        'only_obtained': only_obtained,
    }

    return render(request, 'characters/calculate.html', data)

@login_required
def my_characters(request):
    characters = UserCharacter.objects.filter(user=request.user)
    plans = PlannedCharacter.objects.filter(user=request.user)
    data={
        'characters': characters,
        'plans': plans,
    }
    return render(request, 'characters/my_characters.html', data)


@login_required
def add_my_character(request):
    error=''
    if request.method == "POST":
        form = UserCharacterForm(request.POST, user=request.user)
        if form.is_valid():
            character=form.save(commit=False)
            character.user=request.user
            character.set_talent_levels([
                form.cleaned_data['talent1'],
                form.cleaned_data['talent2'],
                form.cleaned_data['talent3']
            ])
            character.set_target_talent_levels([
                form.cleaned_data['target1'],
                form.cleaned_data['target2'],
                form.cleaned_data['target3']
            ])
            character.save()
            return redirect('/characters/my')
        else:
            error=form.errors

    form=UserCharacterForm(user=request.user)
    data={
        'form':form,
        'error':error
    }
    return render(request, 'characters/add_my.html', data)


@login_required
def add_plan_character(request):
    error=''
    if request.method == "POST":
        form = PlannedCharacterForm(request.POST, user=request.user)
        if form.is_valid():
            character=form.save(commit=False)
            character.user=request.user

            character.set_target_talent_levels([
                form.cleaned_data['target1'],
                form.cleaned_data['target2'],
                form.cleaned_data['target3']
            ])
            character.save()
            return redirect('/characters/my')
        else:
            error=form.errors

    form=PlannedCharacterForm(user=request.user)
    data={
        'form':form,
        'error':error
    }
    return render(request, 'characters/add_plan.html', data)


@login_required
def add_planned_character(request):
    error = ''
    if request.method == "POST":
        form = ExPlannedCharacterForm(request.POST, user=request.user)
        if form.is_valid():
            character = form.save(commit=False)
            character.user = request.user
            character.set_talent_levels([
                form.cleaned_data['talent1'],
                form.cleaned_data['talent2'],
                form.cleaned_data['talent3']
            ])
            character.set_target_talent_levels([
                form.cleaned_data['target1'],
                form.cleaned_data['target2'],
                form.cleaned_data['target3']
            ])
            character.save()

            PlannedCharacter.objects.filter(
                user=request.user,
                name=character.name  # тот же персонаж
            ).delete()

            return redirect('/characters/my')
        else:
            error = form.errors

    form = ExPlannedCharacterForm(user=request.user)
    data = {
        'form': form,
        'error': error
    }
    return render(request, 'characters/add_planned.html', data)


@ensure_csrf_cookie
@login_required
def get_planned_talents(request, character_id):
    try:
        planned_char = PlannedCharacter.objects.filter(
            user=request.user,
            name_id=character_id
        ).first()

        if planned_char and planned_char.target_talent_levels:
            return JsonResponse({
                'talents': planned_char.target_talent_levels
            })
        else:
            return JsonResponse({'talents': [1, 9, 9]})  # дефолтные значения

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def update_character(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        character_type = data['character_type']
        character_id = data['character_id']
        field = data['field']
        value = data['value']

        if character_type == 'usercharacter':
            char = get_object_or_404(UserCharacter, id=character_id, user=request.user)
            if field == 'level':
                char.level = value
            elif field == 'is_ascended':
                char.is_ascended = bool(value)
            elif field == 'talent_normal':
                char.talent_levels[0] = value
            elif field == 'talent_skill':
                char.talent_levels[1] = value
            elif field == 'talent_burst':
                char.talent_levels[2] = value
            elif field.startswith('target_'):
                idx = {'normal': 0, 'skill': 1, 'burst': 2}[field.split('_')[1]]
                char.target_talent_levels[idx] = value
            char.save()

        elif character_type == 'plannedcharacter':
            char = get_object_or_404(PlannedCharacter, id=character_id, user=request.user)
            idx = {'normal': 0, 'skill': 1, 'burst': 2}[field.split('_')[1]]
            char.target_talent_levels[idx] = value
            char.save()

        return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error'}, status=400)


@login_required
@csrf_exempt
def update_inventory_api(request):
    print("REQUEST BODY:", request.body)
    if request.method == 'POST':
        data = json.loads(request.body)
        count = max(0, int(data['count']))  # Валидация
        material_type = data['material_type']
        material_id = data['material_id']

        # UserInventory.get_or_create + update count
        inv, created = UserInventory.objects.get_or_create(
            user=request.user,
            **{material_type + '_id': material_id},
            defaults={'count': count}
        )
        if not created:
            inv.count = count
            inv.save()

        return JsonResponse({'status': 'ok', 'count': count})

