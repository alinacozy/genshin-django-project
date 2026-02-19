from django.urls import path
from . import views

urlpatterns = [
    path('', views.characters_home, name='characters_home' ),
    path('create/', views.create, name='create'),
    path('<int:pk>/update', views.CharacterUpdateView.as_view(), name='character_update' ),
    path('calculate/', views.calculate, name='calculate' ),
    path('my/', views.my_characters, name='my_characters' ),
]