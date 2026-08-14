"""
BlenderToMob Cutting Operators — Operadores para cálculo e exportação do Plano de Corte (Nesting)
"""

import bpy  # type: ignore
from bpy_extras.io_utils import ExportHelper  # type: ignore
from ..cutting.nesting import optimize_nesting
from ..cutting.part_extractor import extract_parts_from_scene
from ..cutting.json_exporter import export_cut_plan_to_json


class BTM_OT_CalculateNesting(bpy.types.Operator):
    """Calcula a otimização de corte (nesting) de todas as peças e módulos na cena"""
    bl_idname = "btm.calculate_nesting"
    bl_label = "Calcular Plano de Corte"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        mdf_cfg = getattr(scene.btm_settings, 'mdf_config', None)

        sheet_w = (mdf_cfg.sheet_width * 1000.0) if mdf_cfg else 2750.0
        sheet_h = (mdf_cfg.sheet_height * 1000.0) if mdf_cfg else 1830.0
        ref_top = (mdf_cfg.refilo_top * 1000.0) if mdf_cfg else 10.0
        ref_bot = (mdf_cfg.refilo_bottom * 1000.0) if mdf_cfg else 10.0
        ref_left = (mdf_cfg.refilo_left * 1000.0) if mdf_cfg else 10.0
        ref_right = (mdf_cfg.refilo_right * 1000.0) if mdf_cfg else 10.0
        kerf = (mdf_cfg.kerf * 1000.0) if mdf_cfg else 4.0
        allow_rot = mdf_cfg.allow_rotation if mdf_cfg else True
        respect_gr = mdf_cfg.respect_grain if mdf_cfg else True

        # Extração inteligente de peças dos módulos da cena
        parts = extract_parts_from_scene(context)

        if not parts:
            self.report({'WARNING'}, "Nenhum módulo ou componente de marcenaria encontrado na cena.")
            return {'CANCELLED'}

        # Execução do algoritmo de nesting
        result = optimize_nesting(
            parts=parts,
            sheet_width=sheet_w,
            sheet_height=sheet_h,
            refilo_top=ref_top,
            refilo_bottom=ref_bot,
            refilo_left=ref_left,
            refilo_right=ref_right,
            kerf=kerf,
            allow_rotation=allow_rot,
            respect_grain=respect_gr
        )

        stats = result["stats"]
        summary = (
            f"Plano de Corte Concluído: {stats['sheets_count']} chapa(s) MDF ({stats['total_placed_parts']} peças). "
            f"Aproveitamento: {stats['utilization_percentage']}% | "
            f"Área Útil: {stats['total_placed_area_m2']} m²"
        )

        scene["btm_nesting_result"] = summary
        scene["btm_nesting_parts_count"] = len(parts)
        scene["btm_nesting_sheets_count"] = stats["sheets_count"]
        scene["btm_nesting_utilization"] = stats["utilization_percentage"]

        # Cache dos dados brutos para exportação
        import json
        scene["btm_nesting_json_cache"] = json.dumps({
            "stats": stats,
            "sheets": result["sheets"],
            "unplaced": result["unplaced"]
        })

        self.report({'INFO'}, summary)
        return {'FINISHED'}


class BTM_OT_ExportCutPlanJSON(bpy.types.Operator, ExportHelper):
    """Exporta o plano de corte e a lista de peças em formato JSON universal (CorteCloud / CutList)"""
    bl_idname = "btm.export_cut_plan_json"
    bl_label = "Exportar Plano de Corte (JSON)"
    bl_options = {'REGISTER'}

    filename_ext = ".json"
    filter_glob: bpy.props.StringProperty(  # type: ignore
        default="*.json",
        options={'HIDDEN'},
        maxlen=255,
    )

    def execute(self, context):
        import json
        scene = context.scene
        cached_data_str = scene.get("btm_nesting_json_cache", "")

        if not cached_data_str:
            # Se não houver cálculo recente, calcula primeiro
            bpy.ops.btm.calculate_nesting()
            cached_data_str = scene.get("btm_nesting_json_cache", "")

        if not cached_data_str:
            self.report({'ERROR'}, "Não foi possível gerar dados de plano de corte para exportar.")
            return {'CANCELLED'}

        nesting_result = json.loads(cached_data_str)
        parts = extract_parts_from_scene(context)

        project_name = scene.name
        if hasattr(scene, 'blendertomob_project') and hasattr(scene.blendertomob_project, 'project_name'):
            project_name = scene.blendertomob_project.project_name or scene.name

        out_path = export_cut_plan_to_json(
            filepath=self.filepath,
            nesting_result=nesting_result,
            parts_list=parts,
            project_name=project_name
        )

        self.report({'INFO'}, f"Plano de Corte exportado com sucesso: {out_path}")
        return {'FINISHED'}


classes = (
    BTM_OT_CalculateNesting,
    BTM_OT_ExportCutPlanJSON,
)


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
