from django.contrib.auth.decorators import login_required
from django.shortcuts import render

def index(request):
     data = {
        'title': 'Главная страница',
        'values': ['alina', 'winky', 'cozy'],
        'obj': {
            'name': 'Winky',
            'age': 3,
            'sex': "female",
        }
     }
     return render(request, 'main/index.html', data)

def about(request):
    return render(request, 'main/about.html')

@login_required
def profile(request):
    return render(request, 'main/profile.html')
