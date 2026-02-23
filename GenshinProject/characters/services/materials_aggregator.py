from ..models import MobMaterial, TalentMaterial, WeeklyMaterial, Stone, ElementChoices, RegionChoices, Specialty, \
    BossMaterial, UserInventory
from .materials_calculator import RequiredMaterials
import dataclasses
from django.contrib.auth.models import User


@dataclasses.dataclass
class MobMaterialAggregated:
    material_1: MobMaterial
    material_2: MobMaterial
    material_3: MobMaterial
    count_1: int
    count_2: int
    count_3: int
    count_my_1: int
    count_my_2: int
    count_my_3: int
    equivalent: int

    @property
    def remain_1(self) -> int:
        return self.count_1 - self.count_my_1

    @property
    def remain_2(self) -> int:
        return self.count_2 - self.count_my_2

    @property
    def remain_3(self) -> int:
        return self.count_3 - self.count_my_3

    @property
    def equivalent_remain(self) -> int:
        return 9*self.remain_3+3*self.remain_2+self.remain_1


@dataclasses.dataclass
class WeeklyMaterialAggregated:
    material_1: WeeklyMaterial
    material_2: WeeklyMaterial
    material_3: WeeklyMaterial
    count_1: int
    count_2: int
    count_3: int
    count_my_1: int
    count_my_2: int
    count_my_3: int
    equivalent: int

    @property
    def remain_1(self) -> int:
        return self.count_1 - self.count_my_1

    @property
    def remain_2(self) -> int:
        return self.count_2 - self.count_my_2

    @property
    def remain_3(self) -> int:
        return self.count_3 - self.count_my_3

    @property
    def equivalent_remain(self) -> int:
        return self.remain_3+self.remain_2+self.remain_1


@dataclasses.dataclass
class TalentMaterialAggregated:
    material_1: TalentMaterial
    material_2: TalentMaterial
    material_3: TalentMaterial
    count_1: int
    count_2: int
    count_3: int
    count_my_1: int
    count_my_2: int
    count_my_3: int
    equivalent: int
    @property
    def remain_1(self) -> int:
        return self.count_1 - self.count_my_1

    @property
    def remain_2(self) -> int:
        return self.count_2 - self.count_my_2

    @property
    def remain_3(self) -> int:
        return self.count_3 - self.count_my_3

    @property
    def equivalent_remain(self) -> int:
        return 9*self.remain_3+3*self.remain_2+self.remain_1

@dataclasses.dataclass
class TalentRegionAggregated:
    material_monday: TalentMaterialAggregated
    material_tuesday: TalentMaterialAggregated
    material_wednesday: TalentMaterialAggregated
    equivalent: int

    @property
    def equivalent_remain(self) -> int:
        return (self.material_monday.equivalent_remain +
                self.material_tuesday.equivalent_remain +
                self.material_wednesday.equivalent_remain)


@dataclasses.dataclass
class StoneAggregated:
    material_1: Stone
    material_2: Stone
    material_3: Stone
    material_4: Stone
    count_1: int
    count_2: int
    count_3: int
    count_4: int
    count_my_1: int
    count_my_2: int
    count_my_3: int
    count_my_4: int
    equivalent: int

    @property
    def remain_1(self) -> int:
        return self.count_1 - self.count_my_1

    @property
    def remain_2(self) -> int:
        return self.count_2 - self.count_my_2

    @property
    def remain_3(self) -> int:
        return self.count_3 - self.count_my_3

    @property
    def remain_4(self) -> int:
        return self.count_4 - self.count_my_4

    @property
    def equivalent_remain(self) -> int:
        return 27*self.remain_4 + 9 * self.remain_3 + 3 * self.remain_2 + self.remain_1


@dataclasses.dataclass
class BossAggregated:
    boss_material: BossMaterial
    count: int
    count_my: int

    @property
    def remain(self) -> int:
        return self.count - self.count_my


@dataclasses.dataclass
class SpecialtyAggregated:
    specialty: Specialty
    count: int
    count_my: int

    @property
    def remain(self) -> int:
        return self.count - self.count_my


@dataclasses.dataclass
class AggregatedMaterials:
    mob_materials: dict[str, MobMaterialAggregated]
    weekly_materials: dict[str, WeeklyMaterialAggregated]
    talent_materials: dict[str, TalentRegionAggregated]
    stones: dict[str, StoneAggregated]
    specialties: list[SpecialtyAggregated]
    boss_materials: list[BossAggregated]


class MaterialsAggregator:
    def aggregate_materials(self, required_materials: RequiredMaterials, request_user: User) -> AggregatedMaterials:

        return AggregatedMaterials(
            mob_materials=self.aggregate_mobs(required_materials.mob_materials, request_user),
            weekly_materials=self.aggregate_weekly(required_materials.weekly_materials, request_user),
            talent_materials=self.aggregate_talents(required_materials.talent_materials, request_user),
            stones=self.aggregate_stones(required_materials.stones, request_user),
            specialties=self.aggregate_specialties(required_materials.specialties, request_user),
            boss_materials=self.aggregate_bosses(required_materials.boss_materials, request_user),
        )

    def aggregate_bosses(self, boss_materials: dict[BossMaterial, int], request_user: User) -> list[BossAggregated]:
        result=[]
        for boss_material in boss_materials:
            result.append(BossAggregated(
                boss_material=boss_material,
                count=boss_materials[boss_material],
                count_my=UserInventory.get_material_count(request_user, boss_material),
            ))

        result.sort(key=lambda b: b.remain, reverse=True)
        return result

    def aggregate_specialties(self, specialties: dict[Specialty, int], request_user: User) -> list[SpecialtyAggregated]:
        result=[]
        for specialty in specialties:
            result.append(SpecialtyAggregated(
                specialty=specialty,
                count=specialties[specialty],
                count_my=UserInventory.get_material_count(request_user, specialty),
            ))

        result.sort(key=lambda b: b.remain, reverse=True)
        return result

    def aggregate_mobs(self, mob_materials: dict[MobMaterial, int], request_user: User) -> dict[str, MobMaterialAggregated]:
        materials_by_mob = dict[str, dict[int, MobMaterial]]()
        for mob_material in mob_materials:
            if mob_material.mob_name not in materials_by_mob:
                materials_by_mob[mob_material.mob_name] = dict()
            materials_by_mob[mob_material.mob_name][mob_material.rarity] = mob_material

        result = dict[str, MobMaterialAggregated]()
        for mob_name, materials_by_rarity in materials_by_mob.items():
            result[mob_name] = MobMaterialAggregated(
                material_1=materials_by_rarity.get(1),
                material_2=materials_by_rarity.get(2),
                material_3=materials_by_rarity.get(3),
                count_1=mob_materials.get(materials_by_rarity.get(1)),
                count_2=mob_materials.get(materials_by_rarity.get(2)),
                count_3=mob_materials.get(materials_by_rarity.get(3)),
                count_my_1=UserInventory.get_material_count(request_user, materials_by_rarity.get(1)),
                count_my_2=UserInventory.get_material_count(request_user, materials_by_rarity.get(2)),
                count_my_3=UserInventory.get_material_count(request_user, materials_by_rarity.get(3)),
                equivalent=(
                        9 * mob_materials.get(materials_by_rarity.get(3)) +
                        3 * mob_materials.get(materials_by_rarity.get(2)) +
                        mob_materials.get(materials_by_rarity.get(1))
                ),
            )
        result = dict(sorted(result.items(), key=lambda item: item[1].equivalent_remain, reverse=True))
        return result

    def aggregate_weekly(self, weekly_materials: dict[WeeklyMaterial, int], request_user: User) -> dict[str, WeeklyMaterialAggregated]:
        materials_by_boss = dict[str, list[WeeklyMaterial]]()
        for weekly_material in weekly_materials:
            if weekly_material.boss_name not in materials_by_boss:
                materials_by_boss[weekly_material.boss_name] = []
            materials_by_boss[weekly_material.boss_name].append(weekly_material)

        result = dict[str, WeeklyMaterialAggregated]()
        for boss_name, materials_by_boss_name in materials_by_boss.items():
            padded = materials_by_boss_name + [None] * (3 - len(materials_by_boss_name)) # чтобы для каждого босса было 3 элемента
            result[boss_name] = WeeklyMaterialAggregated(
                material_1=padded[0],
                material_2=padded[1],
                material_3=padded[2],
                count_1=weekly_materials.get(padded[0], 0),
                count_2=weekly_materials.get(padded[1], 0),
                count_3=weekly_materials.get(padded[2], 0),
                count_my_1=UserInventory.get_material_count(request_user, padded[0]),
                count_my_2=UserInventory.get_material_count(request_user, padded[1]),
                count_my_3=UserInventory.get_material_count(request_user, padded[2]),
                equivalent=(
                        weekly_materials.get(padded[0], 0) +
                        weekly_materials.get(padded[1], 0) +
                        weekly_materials.get(padded[2], 0)
                ),
            )
        print(result)
        result = dict(sorted(result.items(), key=lambda item: item[1].equivalent_remain, reverse=True))
        return result

    def aggregate_talents(self, talent_materials: dict[TalentMaterial, int], request_user: User) -> dict[str, TalentRegionAggregated]:
        materials_by_regweek = dict[tuple[str, int], dict[int, TalentMaterial]]()
        for talent_material in talent_materials:
            if (talent_material.region, talent_material.weekday) not in materials_by_regweek:
                materials_by_regweek[(talent_material.region, talent_material.weekday)] = dict()
            materials_by_regweek[(talent_material.region, talent_material.weekday)][talent_material.rarity] = talent_material
        unique_regions={reg for (reg, _) in materials_by_regweek}
        result = dict[str, TalentRegionAggregated]()
        for reg in unique_regions:
            monday_equivalent = (
                    9 * talent_materials.get(materials_by_regweek.get((reg, 1), {}).get(4), 0) +
                    3 * talent_materials.get(materials_by_regweek.get((reg, 1), {}).get(3), 0) +
                    talent_materials.get(materials_by_regweek.get((reg, 1), {}).get(2), 0)
            )
            tuesday_equivalent = (
                    9 * talent_materials.get(materials_by_regweek.get((reg, 2), {}).get(4), 0) +
                    3 * talent_materials.get(materials_by_regweek.get((reg, 2), {}).get(3), 0) +
                    talent_materials.get(materials_by_regweek.get((reg, 2), {}).get(2), 0)
            )
            wednesday_equivalent = (
                    9 * talent_materials.get(materials_by_regweek.get((reg, 3), {}).get(4), 0) +
                    3 * talent_materials.get(materials_by_regweek.get((reg, 3), {}).get(3), 0) +
                    talent_materials.get(materials_by_regweek.get((reg, 3), {}).get(2), 0)
            )

            result[RegionChoices(reg).label] = TalentRegionAggregated(
                material_monday = TalentMaterialAggregated(
                    material_1=materials_by_regweek.get((reg, 1), {}).get(2),
                    material_2=materials_by_regweek.get((reg, 1), {}).get(3),
                    material_3=materials_by_regweek.get((reg, 1), {}).get(4),
                    count_1=talent_materials.get(materials_by_regweek.get((reg, 1), {}).get(2), 0),
                    count_2=talent_materials.get(materials_by_regweek.get((reg, 1), {}).get(3), 0),
                    count_3=talent_materials.get(materials_by_regweek.get((reg, 1), {}).get(4), 0),
                    count_my_1=UserInventory.get_material_count(request_user, materials_by_regweek.get((reg, 1), {}).get(2)),
                    count_my_2=UserInventory.get_material_count(request_user, materials_by_regweek.get((reg, 1), {}).get(3)),
                    count_my_3=UserInventory.get_material_count(request_user, materials_by_regweek.get((reg, 1), {}).get(4)),
                    equivalent=monday_equivalent,
                ),
                material_tuesday = TalentMaterialAggregated(
                    material_1=materials_by_regweek.get((reg, 2), {}).get(2),
                    material_2=materials_by_regweek.get((reg, 2), {}).get(3),
                    material_3=materials_by_regweek.get((reg, 2), {}).get(4),
                    count_1=talent_materials.get(materials_by_regweek.get((reg, 2), {}).get(2), 0),
                    count_2=talent_materials.get(materials_by_regweek.get((reg, 2), {}).get(3), 0),
                    count_3=talent_materials.get(materials_by_regweek.get((reg, 2), {}).get(4), 0),
                    count_my_1=UserInventory.get_material_count(request_user,
                                                                materials_by_regweek.get((reg, 2), {}).get(2)),
                    count_my_2=UserInventory.get_material_count(request_user,
                                                                materials_by_regweek.get((reg, 2), {}).get(3)),
                    count_my_3=UserInventory.get_material_count(request_user,
                                                                materials_by_regweek.get((reg, 2), {}).get(4)),
                    equivalent=tuesday_equivalent,
                ),
                material_wednesday = TalentMaterialAggregated(
                    material_1=materials_by_regweek.get((reg, 3), {}).get(2),
                    material_2=materials_by_regweek.get((reg, 3), {}).get(3),
                    material_3=materials_by_regweek.get((reg, 3), {}).get(4),
                    count_1=talent_materials.get(materials_by_regweek.get((reg, 3), {}).get(2), 0),
                    count_2=talent_materials.get(materials_by_regweek.get((reg, 3), {}).get(3), 0),
                    count_3=talent_materials.get(materials_by_regweek.get((reg, 3), {}).get(4), 0),
                    count_my_1=UserInventory.get_material_count(request_user,
                                                                materials_by_regweek.get((reg, 3), {}).get(2)),
                    count_my_2=UserInventory.get_material_count(request_user,
                                                                materials_by_regweek.get((reg, 3), {}).get(3)),
                    count_my_3=UserInventory.get_material_count(request_user,
                                                                materials_by_regweek.get((reg, 3), {}).get(4)),
                    equivalent=wednesday_equivalent,
                ),
                equivalent = monday_equivalent+tuesday_equivalent+wednesday_equivalent,
            )


        result = dict(sorted(result.items(), key=lambda item: item[1].equivalent_remain, reverse=True))
        return result

    def aggregate_stones(self, stones: dict[Stone, int], request_user: User) -> dict[str, StoneAggregated]:
        stones_by_element = dict[str, dict[int, Stone]]()
        for stone in stones:
            if stone.element not in stones_by_element:
                stones_by_element[stone.element] = dict()
            stones_by_element[stone.element][stone.rarity] = stone

        result = dict[str, StoneAggregated]()
        for element, materials_by_rarity in stones_by_element.items():
            result[ElementChoices(element).label] = StoneAggregated(
                material_1=materials_by_rarity.get(2),
                material_2=materials_by_rarity.get(3),
                material_3=materials_by_rarity.get(4),
                material_4=materials_by_rarity.get(5),
                count_1=stones.get(materials_by_rarity.get(2)),
                count_2=stones.get(materials_by_rarity.get(3)),
                count_3=stones.get(materials_by_rarity.get(4)),
                count_4=stones.get(materials_by_rarity.get(5)),
                count_my_1=UserInventory.get_material_count(request_user, materials_by_rarity.get(2)),
                count_my_2=UserInventory.get_material_count(request_user, materials_by_rarity.get(3)),
                count_my_3=UserInventory.get_material_count(request_user, materials_by_rarity.get(4)),
                count_my_4=UserInventory.get_material_count(request_user, materials_by_rarity.get(5)),
                equivalent=(
                        27 * stones.get(materials_by_rarity.get(5)) +
                        9 * stones.get(materials_by_rarity.get(4)) +
                        3 * stones.get(materials_by_rarity.get(3)) +
                        stones.get(materials_by_rarity.get(2))
                ),
            )
        result = dict(sorted(result.items(), key=lambda item: item[1].equivalent, reverse=True))
        return result
