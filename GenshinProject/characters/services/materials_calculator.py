from collections import defaultdict
import dataclasses

from ..models import MobMaterial


@dataclasses.dataclass
class RequiredMaterials:
    boss_materials : defaultdict = dataclasses.field(default_factory=lambda: defaultdict(int))
    specialties : defaultdict = dataclasses.field(default_factory=lambda: defaultdict(int))
    stones : defaultdict = dataclasses.field(default_factory=lambda: defaultdict(int))
    mob_materials : defaultdict[MobMaterial, int] = dataclasses.field(default_factory=lambda: defaultdict(int))
    weekly_materials : defaultdict = dataclasses.field(default_factory=lambda: defaultdict(int))
    talent_materials : defaultdict = dataclasses.field(default_factory=lambda: defaultdict(int))


    def merge_with(self, other: 'RequiredMaterials'):
        """Складывает материалы из другого RequiredMaterials"""
        for field_name in dataclasses.fields(self):
            group1 = getattr(self, field_name.name)
            group2 = getattr(other, field_name.name)
            for mat_name, count in group2.items():
                group1[mat_name] = group1.get(mat_name, 0) + count

    def __str__(self):
        return f"{self.mob_materials}, {self.specialties}, {self.stones}, {self.talent_materials}, {self.weekly_materials}, {self.talent_materials}"


class MaterialsCalculator:

    def calculate_all(self, characters) -> RequiredMaterials:
        total = RequiredMaterials()
        for char in characters:
            char_mats = self.calculate_character(char)
            total.merge_with(char_mats)
        return total

    def calculate_character(self, user_character) -> RequiredMaterials:
        result = RequiredMaterials()

        # считаем сколько возвышений уже выполнено
        ascensions=self._calculate_ascensions(user_character.level, user_character.is_ascended)

        # материалы босса
        num_boss = self._get_num_boss_materials(ascensions)
        result.boss_materials[user_character.name.boss_material] = num_boss

        # диковинки
        num_spec = self._get_num_specialties(ascensions)
        result.specialties[user_character.name.specialty] = num_spec

        # камни
        num_stones = self._get_num_stones(ascensions)
        stones=user_character.name.get_stones()
        for stone in stones:
            result.stones[stone] = num_stones[stone.rarity]

        # еженедельные материалы
        num_weekly = self._get_num_weekly_materials(user_character)
        result.weekly_materials[user_character.name.weekly_material] = num_weekly

        # материалы талантов
        num_talent_materials = self._get_num_talent_materials(user_character)
        talent_materials=user_character.name.get_talent_materials()
        for material in talent_materials:
            result.talent_materials[material] += num_talent_materials[material.rarity]

        # материалы с мобов
        num_mob_materials = self._get_num_mob_materials(user_character, ascensions)
        mob_materials=user_character.name.get_mob_materials()
        for mob_material in mob_materials:
            result.mob_materials[mob_material] += num_mob_materials[mob_material.rarity]

        return result

    def _calculate_ascensions(self, level: int, is_ascended: bool = False) -> int:
        boundaries = [20, 40, 50, 60, 70, 80]

        # Корректировка на границе
        if level in boundaries and not is_ascended:
            level -= 1

        # Сколько границ пройдено?
        return min(sum(1 for b in boundaries if b <= level), 6)


    def _get_num_boss_materials(self, ascensions) -> int :
        num_boss_materials = 0
        boss_for_ascension = [0,2,4,8,12,20]
        for i in range(ascensions, 6):
            num_boss_materials += boss_for_ascension[i]
        return num_boss_materials

    def _get_num_specialties(self, ascensions) -> int:
        num_specialties = 0
        specialties_for_ascension = [3,10,20,30,45,60]
        for i in range(ascensions, 6):
            num_specialties += specialties_for_ascension[i]
        return num_specialties

    def _get_num_stones(self, ascensions) -> defaultdict[int, int]:
        num_stones = defaultdict(int)
        stones_for_ascensions = [
            {'rarity': 2, 'count': 1},
            {'rarity': 3, 'count': 3},
            {'rarity': 3, 'count': 6},
            {'rarity': 4, 'count': 3},
            {'rarity': 4, 'count': 6},
            {'rarity': 5, 'count': 6},
        ]
        for asc in range(ascensions, 6):
            stone_for_ascension = stones_for_ascensions[asc]
            num_stones[stone_for_ascension['rarity']] += stone_for_ascension['count']
        return num_stones


    def _get_num_weekly_materials(self, user_character) -> int:
        num_weekly = 0
        weekly_for_level = [0, 0, 0, 0, 0, 0, 1, 1, 2, 2]
        for i in range(3):
            for level in range(user_character.talent_levels[i], user_character.target_talent_levels[i] + 1):
                num_weekly += weekly_for_level[level]
        return num_weekly

    def _get_num_talent_materials(self, user_character) -> defaultdict[int, int]:
        num_books = defaultdict(int)
        books_for_levels = [
            {'rarity': 2, 'count': 3}, # на 2 уровень = 0 индекс
            {'rarity': 3, 'count': 2}, # на 3 уровень
            {'rarity': 3, 'count': 4},
            {'rarity': 3, 'count': 6},
            {'rarity': 3, 'count': 9},
            {'rarity': 4, 'count': 4},
            {'rarity': 4, 'count': 6},
            {'rarity': 4, 'count': 12},
            {'rarity': 4, 'count': 16},
        ]
        for i in range(3): # для каждого таланта
            for level in range(user_character.talent_levels[i], user_character.target_talent_levels[i]):
                books_for_level=books_for_levels[level - 1]
                num_books[books_for_level['rarity']] += books_for_level['count']
        return num_books

    def _get_num_mob_materials(self, user_character, ascensions) -> defaultdict[int, int]:
        num_mob_materials = defaultdict(int)

        # --- для возвышений ---
        mobs_for_ascensions = [
            {'rarity': 1, 'count': 3},
            {'rarity': 1, 'count': 15},
            {'rarity': 2, 'count': 12},
            {'rarity': 2, 'count': 18},
            {'rarity': 3, 'count': 12},
            {'rarity': 3, 'count': 24},
        ]
        for asc in range(ascensions, 6):
            mob_for_ascension = mobs_for_ascensions[asc]
            num_mob_materials[mob_for_ascension['rarity']] += mob_for_ascension['count']

        # --- для талантов ---
        mobs_for_levels = [
            {'rarity': 1, 'count': 6},  # на 2 уровень = 0 индекс
            {'rarity': 2, 'count': 3},  # на 3 уровень
            {'rarity': 2, 'count': 4},
            {'rarity': 2, 'count': 6},
            {'rarity': 2, 'count': 9},
            {'rarity': 3, 'count': 4},
            {'rarity': 3, 'count': 6},
            {'rarity': 3, 'count': 9},
            {'rarity': 3, 'count': 12},
        ]
        for i in range(3):
            for level in range(user_character.talent_levels[i], user_character.target_talent_levels[i]):
               mobs_for_level=mobs_for_levels[level - 1]
               num_mob_materials[mobs_for_level['rarity']] += mobs_for_level['count']

        return num_mob_materials
