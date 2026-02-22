from ..models import MobMaterial, TalentMaterial
from .materials_calculator import RequiredMaterials
import dataclasses


@dataclasses.dataclass
class MobMaterialAggregated:
    material_1: MobMaterial
    material_2: MobMaterial
    material_3: MobMaterial
    count_1: int
    count_2: int
    count_3: int
    equivalent: int


@dataclasses.dataclass
class TalentMaterialAggregated:
    material_1: TalentMaterial
    material_2: TalentMaterial
    material_3: TalentMaterial
    count_1: int
    count_2: int
    count_3: int
    equivalent: int

@dataclasses.dataclass
class TalentRegionAggregated:
    material_monday: TalentMaterialAggregated
    material_tuesday: TalentMaterialAggregated
    material_wednesday: TalentMaterialAggregated
    equivalent: int

@dataclasses.dataclass
class AggregatedMaterials:
    mob_materials: dict[str, MobMaterialAggregated]
    talent_materials: dict[str, TalentRegionAggregated]


class MaterialsAggregator:
    def aggregate_materials(self, required_materials: RequiredMaterials) -> AggregatedMaterials:

        return AggregatedMaterials(
            mob_materials=self.aggregate_mobs(required_materials.mob_materials),
            talent_materials=self.aggregate_talents(required_materials.talent_materials),
        )

    def aggregate_mobs(self, mob_materials: dict[MobMaterial, int]) -> dict[str, MobMaterialAggregated]:
        materials_by_mob = dict[str, dict[int, MobMaterial]]()
        for mob_material in mob_materials:
            if mob_material.mob_name not in materials_by_mob:
                materials_by_mob[mob_material.mob_name] = dict()
            materials_by_mob[mob_material.mob_name][mob_material.rarity] = mob_material
        print(materials_by_mob)

        result = dict[str, MobMaterialAggregated]()
        for mob_name, materials_by_rarity in materials_by_mob.items():
            result[mob_name] = MobMaterialAggregated(
                material_1=materials_by_rarity[1],
                material_2=materials_by_rarity[2],
                material_3=materials_by_rarity[3],
                count_1=mob_materials[materials_by_rarity[1]],
                count_2=mob_materials[materials_by_rarity[2]],
                count_3=mob_materials[materials_by_rarity[3]],
                equivalent=(
                        9 * mob_materials[materials_by_rarity[3]] +
                        3 * mob_materials[materials_by_rarity[2]] +
                        mob_materials[materials_by_rarity[1]]
                ),
            )
        result = dict(sorted(result.items(), key=lambda item: item[1].equivalent, reverse=True))
        return result

    def aggregate_talents(self, talent_materials: dict[TalentMaterial, int]) -> dict[str, TalentRegionAggregated]:
        materials_by_regweek = dict[tuple[str, int], dict[int, TalentMaterial]]()
        for talent_material in talent_materials:
            if (talent_material.region, talent_material.weekday) not in materials_by_regweek:
                materials_by_regweek[(talent_material.region, talent_material.weekday)] = dict()
            materials_by_regweek[(talent_material.region, talent_material.weekday)][talent_material.rarity] = talent_material
        print(materials_by_regweek)
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

            result[reg] = TalentRegionAggregated(
                material_monday = TalentMaterialAggregated(
                    material_1=materials_by_regweek.get((reg, 1), {}).get(2),
                    material_2=materials_by_regweek.get((reg, 1), {}).get(3),
                    material_3=materials_by_regweek.get((reg, 1), {}).get(4),
                    count_1=talent_materials.get(materials_by_regweek.get((reg, 1), {}).get(2), 0),
                    count_2=talent_materials.get(materials_by_regweek.get((reg, 1), {}).get(3), 0),
                    count_3=talent_materials.get(materials_by_regweek.get((reg, 1), {}).get(4), 0),
                    equivalent=monday_equivalent,
                ),
                material_tuesday = TalentMaterialAggregated(
                    material_1=materials_by_regweek.get((reg, 2), {}).get(2),
                    material_2=materials_by_regweek.get((reg, 2), {}).get(3),
                    material_3=materials_by_regweek.get((reg, 2), {}).get(4),
                    count_1=talent_materials.get(materials_by_regweek.get((reg, 2), {}).get(2), 0),
                    count_2=talent_materials.get(materials_by_regweek.get((reg, 2), {}).get(3), 0),
                    count_3=talent_materials.get(materials_by_regweek.get((reg, 2), {}).get(4), 0),
                    equivalent=tuesday_equivalent,
                ),
                material_wednesday = TalentMaterialAggregated(
                    material_1=materials_by_regweek.get((reg, 3), {}).get(2),
                    material_2=materials_by_regweek.get((reg, 3), {}).get(3),
                    material_3=materials_by_regweek.get((reg, 3), {}).get(4),
                    count_1=talent_materials.get(materials_by_regweek.get((reg, 3), {}).get(2), 0),
                    count_2=talent_materials.get(materials_by_regweek.get((reg, 3), {}).get(3), 0),
                    count_3=talent_materials.get(materials_by_regweek.get((reg, 3), {}).get(4), 0),
                    equivalent=wednesday_equivalent,
                ),
                equivalent = monday_equivalent+tuesday_equivalent+wednesday_equivalent,
            )


        result = dict(sorted(result.items(), key=lambda item: item[1].equivalent, reverse=True))
        return result
