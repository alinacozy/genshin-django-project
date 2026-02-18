from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home' ),
    path('about/', views.about,  name='about'),
    path('profile/', views.profile,  name='profile'),
    path('register/', views.RegisterView.as_view(),  name='register')
]