from django.shortcuts import render, redirect
from .models import Character, UserCharacter
from .forms import CharacterForm
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
    data = {
        'characters': characters,
        'materials': materials
    }
    return render(request, 'characters/calculate.html', data)

def my_characters(request):
    characters = UserCharacter.objects.filter(user=request.user)
    return render(request, 'characters/my_characters.html', {'characters': characters})
