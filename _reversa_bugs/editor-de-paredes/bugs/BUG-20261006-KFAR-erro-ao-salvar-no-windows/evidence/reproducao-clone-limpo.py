import bpy, addon_utils, importlib, traceback
name = next(m.__name__ for m in addon_utils.modules() if m.__name__.endswith('caffmob_draw'))
addon_utils.enable(name, default_set=True)
class P:
    def __getattr__(self, n): return (0.5, 0.5, 0.5, 1.0)
type(bpy.context.window_manager.home_builder).get_user_preferences = lambda self, c: P()
apply = importlib.import_module(name + '.walls2d.apply'); model = importlib.import_module(name + '.walls2d.model')
try:
    apply.apply_plan(bpy.context, model.WallPlan([model.rectangle(10.0, 20.0)]))
    print("RESULTADO: paredes criadas", sum(1 for o in bpy.context.scene.objects if o.get('IS_WALL_BP')))
except Exception as exc:
    print("RESULTADO: ERRO", type(exc).__name__, exc)
