from django.shortcuts import render, redirect
from .models import Character, UserCharacter, UserInventory
from .forms import CharacterForm, UserCharacterForm
from django.views.generic import UpdateView
from django.contrib.auth.decorators import login_required

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
    characters = UserCharacter.objects.filter(user=request.user)
    calculator = MaterialsCalculator()
    materials = calculator.calculate_all(characters)
    aggregated = MaterialsAggregator().aggregate_materials(materials, request_user=request.user)
    data = {
        'characters': characters,
        'aggregated': aggregated,
    }

    return render(request, 'characters/calculate.html', data)

@login_required
def my_characters(request):
    characters = UserCharacter.objects.filter(user=request.user)
    return render(request, 'characters/my_characters.html', {'characters': characters})


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
            return redirect('/characters')
        else:
            error=form.errors

    form=UserCharacterForm(user=request.user)
    data={
        'form':form,
        'error':error
    }
    return render(request, 'characters/create.html', data)



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

