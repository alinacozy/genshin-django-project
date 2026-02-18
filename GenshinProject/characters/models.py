from django.db import models

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


