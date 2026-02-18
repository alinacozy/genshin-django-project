from .models import Character
from django.forms import ModelForm, TextInput, Select

class CharacterForm(ModelForm):
    class Meta:
        model = Character
        fields=['name', 'region', 'element', 'weekly_material']

        widgets = {
            'name': TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Имя персонажа'
            }),
            'region': Select(attrs={
                'class': 'form-control',
            }),
            'element': Select(attrs={
                'class': 'form-control'
            }),
            'weekly_material': Select(attrs={
                'class': 'form-control'
            }),
        }

        labels = {
            'name': 'Имя персонажа',
            'element': 'Элемент',
            'region': 'Регион',
            'weekly_material': 'Еженедельный материал'
        }