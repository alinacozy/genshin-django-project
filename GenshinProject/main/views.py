from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.shortcuts import render
from django.views.generic import CreateView, FormView

from .forms import RegisterForm


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

class RegisterView(FormView):
    form_class = RegisterForm
    template_name = 'registration/register.html'
    success_url = '/profile'


    def form_valid(self, form):
        form.save()
        return super().form_valid(form)

