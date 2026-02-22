from django.shortcuts import render, redirect
from .models import Character, UserCharacter
from .forms import CharacterForm, UserCharacterForm
from django.views.generic import UpdateView
from django.contrib.auth.decorators import login_required

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
    materials_dict = {
        'mob_materials': dict(materials.mob_materials),
        'boss_materials': dict(materials.boss_materials),
        'weekly_materials': dict(materials.weekly_materials),
        'talent_materials': dict(materials.talent_materials),
        'specialties': dict(materials.specialties),
        'stones': dict(materials.stones),
    }

    data = {
        'characters': characters,
        'materials': materials_dict
    }


    return render(request, 'characters/calculate.html', data)

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
