from django.urls import path
from . import views

urlpatterns = [
    path('', views.characters_home, name='characters_home' ),
    path('create/', views.create, name='create'),
    path('<int:pk>/update', views.CharacterUpdateView.as_view(), name='character_update' ),
    path('calculate/', views.calculate, name='calculate' ),
    path('my/', views.my_characters, name='my_characters' ),
    path('add_my/', views.add_my_character, name='add_my_character' ),
    path('add_plan/', views.add_plan_character, name='add_plan_character' ),
    path('add_planned/', views.add_planned_character, name='add_planned_character' ),
    path('get-planned-talents/<int:character_id>/', views.get_planned_talents, name='get_planned_talents'),
    path('inventory/update/', views.update_inventory_api, name='update_inventory'),
    path('update-character/', views.update_character, name='update_character'),
]