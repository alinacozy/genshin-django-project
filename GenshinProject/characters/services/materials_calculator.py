from collections import defaultdict

from ..models import UserCharacter


class MaterialsCalculator:

    def calculate_all(self, characters):

        # Шаг 2: словарь для суммирования
        total_materials = defaultdict(int)

        # Шаг 3: для каждого персонажа
        for char in characters:
            char_materials = self.calculate_character(char)

            # Шаг 4: суммировать по имени материала
            for material_name, count in char_materials.items():
                total_materials[material_name] += count

        return dict(total_materials)

    def calculate_character(self, user_character):
        # Логика подсчета для одного персонажа
        character_materials = defaultdict(int)

        # еженедельные материалы
        num_weekly= self._get_num_weekly_materials(user_character)

        character_materials[user_character.name.weekly_material] = num_weekly
        return character_materials
    
    def _get_num_weekly_materials(self, user_character):
        num_weekly = 0
        weekly_for_level = [0, 0, 0, 0, 0, 0, 1, 1, 2, 2]
        for i in range(3):
            for level in range(user_character.talent_levels[i], user_character.target_talent_levels[i] + 1):
                num_weekly += weekly_for_level[level]
        return num_weekly