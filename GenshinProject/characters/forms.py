from .models import Character, UserCharacter, PlannedCharacter
from django.forms import ModelForm, TextInput, Select, NumberInput
from django import forms

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


class UserCharacterForm(ModelForm):

    talent1 = forms.IntegerField(min_value=1, max_value=10, label="Уровень таланта 1")
    talent2 = forms.IntegerField(min_value=1, max_value=10, label="Уровень таланта 2")
    talent3 = forms.IntegerField(min_value=1, max_value=10, label="Уровень таланта 3")
    target1 = forms.IntegerField(min_value=1, max_value=10, label="Цель таланта 1")
    target2 = forms.IntegerField(min_value=1, max_value=10, label="Цель таланта 2")
    target3 = forms.IntegerField(min_value=1, max_value=10, label="Цель таланта 3")

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

        #фильтруем персонажей
        if user:  # проверяем, что user существует
            existing_chars = UserCharacter.objects.filter(
                user=user
            ).values_list('name_id', flat=True)

            planned_chars = PlannedCharacter.objects.filter(
                user=user
            ).values_list('name_id', flat=True)

            excluded_chars = existing_chars.union(planned_chars)

            self.fields['name'].queryset = Character.objects.exclude(
                id__in=excluded_chars
            )
        else:
            print('user not exist')
            self.fields['name'].queryset = Character.objects.none()

    def clean_name(self):
        selected_character = self.cleaned_data.get('name')
        if UserCharacter.objects.filter(user=self.user, name=selected_character).exists():
            raise forms.ValidationError("У тебя уже есть этот персонаж!")
        return selected_character

    class Meta:
        model = UserCharacter
        fields = ['name', 'level', 'is_ascended', 'talent1', 'talent2', 'talent3', 'target1', 'target2', 'target3']

        widgets = {
            'name': Select(attrs={
                'class': 'form-control',
            }),
            'level': NumberInput(attrs={
                'class': 'form-control',
            }),
            'is_ascended': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            })
        }

        labels = {
            'name': 'Персонаж',
            'level': 'Уровень',
        }


class PlannedCharacterForm(ModelForm):

    target1 = forms.IntegerField(min_value=1, max_value=10, label="Цель таланта 1")
    target2 = forms.IntegerField(min_value=1, max_value=10, label="Цель таланта 2")
    target3 = forms.IntegerField(min_value=1, max_value=10, label="Цель таланта 3")

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

        #фильтруем персонажей
        if user:  # проверяем, что user существует
            existing_chars = UserCharacter.objects.filter(
                user=user
            ).values_list('name_id', flat=True)

            planned_chars = PlannedCharacter.objects.filter(
                user=user
            ).values_list('name_id', flat=True)

            excluded_chars = existing_chars.union(planned_chars)

            self.fields['name'].queryset = Character.objects.exclude(
                id__in=excluded_chars
            )
        else:
            print('user not exist')
            self.fields['name'].queryset = Character.objects.none()

    def clean_name(self):
        selected_character = self.cleaned_data.get('name')
        if UserCharacter.objects.filter(user=self.user, name=selected_character).exists():
            raise forms.ValidationError("У тебя уже есть этот персонаж!")
        return selected_character

    class Meta:
        model = PlannedCharacter
        fields = ['name', 'target1', 'target2', 'target3']

        widgets = {
            'name': Select(attrs={
                'class': 'form-control',
            }),
        }

        labels = {
            'name': 'Персонаж',
        }


class ExPlannedCharacterForm(ModelForm):

    talent1 = forms.IntegerField(min_value=1, max_value=10, label="Уровень таланта 1")
    talent2 = forms.IntegerField(min_value=1, max_value=10, label="Уровень таланта 2")
    talent3 = forms.IntegerField(min_value=1, max_value=10, label="Уровень таланта 3")
    target1 = forms.IntegerField(min_value=1, max_value=10, label="Цель таланта 1")
    target2 = forms.IntegerField(min_value=1, max_value=10, label="Цель таланта 2")
    target3 = forms.IntegerField(min_value=1, max_value=10, label="Цель таланта 3")

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

        #фильтруем персонажей
        if user:  # проверяем, что user существует

            planned_chars = PlannedCharacter.objects.filter(
                user=user
            ).values_list('name_id', flat=True)

            self.fields['name'].queryset = Character.objects.filter(id__in=planned_chars)
        else:
            print('user not exist')
            self.fields['name'].queryset = Character.objects.none()

    def clean_name(self):
        selected_character = self.cleaned_data.get('name')
        if UserCharacter.objects.filter(user=self.user, name=selected_character).exists():
            raise forms.ValidationError("У тебя уже есть этот персонаж!")
        return selected_character

    class Meta:
        model = UserCharacter
        fields = ['name', 'level', 'is_ascended', 'talent1', 'talent2', 'talent3', 'target1', 'target2', 'target3']

        widgets = {
            'name': Select(attrs={
                'class': 'form-control',
                'id': 'id_name',  # для JS
            }),
            'level': NumberInput(attrs={
                'class': 'form-control',
            }),
            'is_ascended': forms.CheckboxInput(attrs={
                'class': 'form-check-input',
            })
        }

        labels = {
            'name': 'Персонаж',
            'level': 'Уровень',
        }