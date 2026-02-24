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

class WeekChoices(models.IntegerChoices):
    MONDAY = 1, 'Понедельник'
    TUESDAY = 2, 'Вторник'
    WEDNESDAY = 3, 'Среда'

class Character(models.Model):
    name = models.CharField("Имя", max_length=100)
    region = models.CharField("Регион", max_length=2, choices=RegionChoices.choices)
    element = models.CharField("Элемент", max_length=1, choices=ElementChoices.choices)
    weekly_material = models.ForeignKey('WeeklyMaterial', verbose_name="Еженедельный материал", on_delete=models.PROTECT, null=True)
    boss_material = models.ForeignKey('BossMaterial', verbose_name="Материал босса",
                                        on_delete=models.PROTECT, null=True)
    talent_weekday = models.IntegerField(
        choices=WeekChoices.choices,
        verbose_name='День недели талантов',
        help_text='День недели, когда фармятся книги талантов',
        null = True
    )
    specialty = models.ForeignKey('Specialty', verbose_name="Диковинка",
                                      on_delete=models.PROTECT, null=True)

    mob = models.ForeignKey(  # храним только имя моба
        'Mob',
        verbose_name="Моб (материалы)",
        on_delete=models.PROTECT,
        help_text="Выберите моба -> получите все его материалы",
        null = True
    )

    def get_mob_materials(self):
        """Получить все 3 материала моба"""
        return MobMaterial.objects.filter(mob_name=self.mob)

    def get_talent_materials(self):
        """
        Возвращает все 3 книги талантов этого персонажа
        """
        return TalentMaterial.objects.filter(
            region=self.region,
            weekday=self.talent_weekday
        ).order_by('rarity')

    def get_stones(self):
        """
        Возвращает необходимые камни возвышения для этого персонажа
        """
        return Stone.objects.filter(
            element=self.element
        ).order_by('rarity')

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


class BossMaterial(models.Model):
    name = models.CharField("Название", max_length=200, db_index=True)
    boss_name = models.CharField("Название босса", max_length=200)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Материал босса'
        verbose_name_plural = 'Материалы босса'


class TalentMaterial(models.Model):
    name = models.CharField("Название", max_length=200, db_index=True)
    region = models.CharField("Регион", max_length=2, choices=RegionChoices.choices)
    rarity = models.IntegerField(
        validators=[
            MinValueValidator(2),
            MaxValueValidator(4)
        ],
        help_text="Редкость книги может быть от 2 до 4 звезд",
        verbose_name="Редкость"
    )
    weekday=models.IntegerField(
        choices=WeekChoices.choices,
        verbose_name='День недели'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Книга талантов'
        verbose_name_plural = 'Книги талантов'


class Specialty(models.Model):
    name = models.CharField("Название", max_length=200, db_index=True)
    region = models.CharField("Регион", max_length=2, choices=RegionChoices.choices)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Диковинка'
        verbose_name_plural = 'Диковинки'


class Stone(models.Model):
    name = models.CharField("Название", max_length=200, db_index=True)
    element = models.CharField("Элемент", max_length=1, choices=ElementChoices.choices)
    rarity = models.IntegerField(
        validators=[
            MinValueValidator(2),
            MaxValueValidator(5)
        ],
        help_text="Редкость камня может быть от 2 до 5 звезд",
        verbose_name="Редкость"
    )

    def __str__(self):
        return f'{self.name} ({self.get_element_display()})'

    class Meta:
        verbose_name = 'Камень'
        verbose_name_plural = 'Камни'


class Mob(models.Model):
    name = models.CharField("Название моба", max_length=200, unique=True, db_index=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Моб'
        verbose_name_plural = 'Мобы'


class MobMaterial(models.Model):
    name = models.CharField("Название", max_length=200, db_index=True)
    mob_name = models.ForeignKey(Mob, on_delete=models.CASCADE, verbose_name="Название моба", max_length=200, db_index=True)
    rarity = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(3)
        ],
        help_text="Редкость материалов с мобов может быть от 1 до 3 звезд",
        verbose_name="Редкость"
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Материал моба'
        verbose_name_plural = 'Материалы мобов'


class UserCharacter(models.Model):
    name = models.ForeignKey("Character", verbose_name="Имя",
                                        on_delete=models.PROTECT, null=True)
    level = models.IntegerField(
        validators=[
            MinValueValidator(1),
            MaxValueValidator(90)
        ],
        help_text="Уровень должен быть от 1 до 90",
        verbose_name='Уровень'
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



class PlannedCharacter(models.Model):
    """Планируемый, но неполученный персонаж"""
    name = models.ForeignKey("Character", verbose_name="Имя",
                                        on_delete=models.PROTECT, null=True)
    level = 1
    is_ascended = False
    talent_levels = [1, 1, 1]
    target_talent_levels = models.JSONField(default=list, verbose_name='Целевые уровни талантов')
    user = models.ForeignKey(User, verbose_name="Пользователь",
                                        on_delete=models.CASCADE, null=True)

    def get_target_talent_levels(self):
        """Получить целевые уровни как список"""
        return self.target_talent_levels or []

    def set_target_talent_levels(self, levels):
        """Установить целевые уровни [normal, skill, burst]"""
        if len(levels) != 3:
            raise ValueError("Нужно ровно 3 числа (1-10)")
        self.target_talent_levels = [max(1, min(10, int(x))) for x in levels]

    def __str__(self):
        return f"{self.name} (не получен)"

    class Meta:
        verbose_name = 'Планируемый персонаж'
        verbose_name_plural = 'Планируемые персонажи'


class UserInventory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inventory')

    # Связь с конкретными моделями материалов
    mob_material = models.ForeignKey('MobMaterial', on_delete=models.SET_NULL, null=True, blank=True)
    boss_material = models.ForeignKey('BossMaterial', on_delete=models.SET_NULL, null=True, blank=True)
    weekly_material = models.ForeignKey('WeeklyMaterial', on_delete=models.SET_NULL, null=True, blank=True)
    talent_material = models.ForeignKey('TalentMaterial', on_delete=models.SET_NULL, null=True, blank=True)
    stone = models.ForeignKey('Stone', on_delete=models.SET_NULL, null=True, blank=True)
    specialty = models.ForeignKey('Specialty', on_delete=models.SET_NULL, null=True, blank=True)

    count = models.IntegerField(default=0, validators=[MinValueValidator(0)])

    class Meta:
        unique_together = ('user', 'mob_material', 'boss_material', 'weekly_material', 'talent_material', 'stone',
                           'specialty')
        verbose_name='Пользовательский материал'
        verbose_name_plural='Пользовательский инвентарь'

    def get_material_name(self):
        """Для шаблона — название материала"""
        if self.mob_material:
            return self.mob_material.name
        elif self.boss_material:
            return self.boss_material.name
        elif self.weekly_material:
            return self.weekly_material.name
        elif self.talent_material:
            return self.talent_material.name
        elif self.stone:
            return self.stone.name
        elif self.specialty:
            return self.specialty.name

        return "Неизвестно"

    def get_material_type(self):
        """Тип материала для группировки"""
        if self.mob_material: return "MobMaterial"
        if self.boss_material: return "BossMaterial"
        if self.weekly_material: return "WeeklyMaterial"
        if self.talent_material: return "TalentMaterial"
        if self.stone: return "Stone"
        if self.specialty: return "Specialty"
        return "Unknown"

    @classmethod
    def get_material_count(cls, user: User, material) -> int:
        """Получить количество материала в инвентаре пользователя"""
        if isinstance(material, MobMaterial):
            inv = cls.objects.filter(user=user, mob_material=material).first()
        elif isinstance(material, BossMaterial):
            inv = cls.objects.filter(user=user, boss_material=material).first()
        elif isinstance(material, WeeklyMaterial):
            inv = cls.objects.filter(user=user, weekly_material=material).first()
        elif isinstance(material, TalentMaterial):
            inv = cls.objects.filter(user=user, talent_material=material).first()
        elif isinstance(material, Stone):
            inv = cls.objects.filter(user=user, stone=material).first()
        elif isinstance(material, Specialty):
            inv = cls.objects.filter(user=user, specialty=material).first()
        else:
            return 0

        return inv.count if inv else 0

    def __str__(self):
        return f"{self.get_material_name()} ({self.get_material_type()}) - {self.count} шт."
