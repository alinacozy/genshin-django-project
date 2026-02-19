from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.contrib.auth.models import User


class RegionChoices(models.TextChoices):
    MONDSTADT = 'MO', 'Мондштадт'
    LIYUE = 'LY', 'Ли Юэ'
    INAZUMA = 'IN', 'Инадзума'
    SUMERU = 'SU', 'Сумеру'
    FONTAINE = 'FO', 'Фонтейн'
    NATLAN = 'NA', 'Натлан'
    NODKRAI = 'NK', 'Нод-Край'
    SNEZHNAYA = 'SN', 'Снежная'

class ElementChoices(models.TextChoices):
    ANEMO = 'A', 'Анемо'
    GEO = 'G', 'Гео'
    ELECTRO = 'E', 'Электро'
    DENDRO = 'D', 'Дендро'
    HYDRO = 'H', 'Гидро'
    PYRO = 'P', 'Пиро'
    CRYO = 'C', 'Крио'

class Character(models.Model):
    name = models.CharField("Имя", max_length=100)
    region = models.CharField("Регион", max_length=2, choices=RegionChoices.choices)
    element = models.CharField("Элемент", max_length=1, choices=ElementChoices.choices)
    weekly_material = models.ForeignKey('WeeklyMaterial', verbose_name="Еженедельный материал", on_delete=models.PROTECT, null=True)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return '/characters'

    class Meta:
        verbose_name = 'Персонаж'
        verbose_name_plural = 'Персонажи'



class WeeklyMaterial(models.Model):
    name = models.CharField("Название", max_length=200, db_index=True)
    boss_name = models.CharField("Название босса", max_length=200)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Еженедельный материал'
        verbose_name_plural = 'Еженедельные материалы'


class UserCharacter(models.Model):
    name = models.ForeignKey("Character", verbose_name="Имя",
                                        on_delete=models.PROTECT, null=True)
    level = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(90)
        ],
        help_text="Уровень должен быть от 1 до 90"
    )
    is_ascended = models.BooleanField(default=False, verbose_name='Возвышен')
    talent_levels = models.JSONField(default=list, verbose_name='Уровни талантов')
    target_talent_levels = models.JSONField(default=list, verbose_name='Целевые уровни талантов')
    user = models.ForeignKey(User, verbose_name="Пользователь",
                                        on_delete=models.CASCADE, null=True)

    def get_talent_levels(self):
        """Получить уровни как список"""
        return self.talent_levels or []

    def set_talent_levels(self, levels):
        """Установить уровни [normal, skill, burst]"""
        if len(levels) != 3:
            raise ValueError("Нужно ровно 3 числа (1-10)")
        self.talent_levels = [max(1, min(10, int(x))) for x in levels]

    def get_target_talent_levels(self):
        """Получить целевые уровни как список"""
        return self.target_talent_levels or []

    def set_target_talent_levels(self, levels):
        """Установить целевые уровни [normal, skill, burst]"""
        if len(levels) != 3:
            raise ValueError("Нужно ровно 3 числа (1-10)")
        self.target_talent_levels = [max(1, min(10, int(x))) for x in levels]

    def __str__(self):
        return f"{self.name}, {self.level} ур."

    class Meta:
        verbose_name = 'Пользовательский персонаж'
        verbose_name_plural = 'Пользовательские персонажи'


