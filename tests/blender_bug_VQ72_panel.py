"""Reprodução e regressão do BUG-20261007-VQ72: medidas do trecho no painel do editor de paredes.

Run: blender --background --factory-startup --python-exit-code 1 --python tests/blender_bug_VQ72_panel.py

Com a cena do Blender em metros e o projeto em milímetros (o padrão de um arquivo novo), o painel do trecho tem de
mostrar e aceitar a unidade da planta.
"""

import sys
import types
from pathlib import Path

import bpy

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _blender_env as env  # noqa: E402,F401
from caffmob_draw.walls2d import model, panels, props  # noqa: E402

ctx = bpy.context
scene = ctx.scene
scene.unit_settings.system = 'METRIC'
scene.unit_settings.length_unit = 'METERS'
assert scene.btm_settings.btm_unit == 'MILLIMETERS', scene.btm_settings.btm_unit

s = props.start(model.WallPlan([model.rectangle(4.0, 3.0)]), scene.name)
s.selected, s.line = (0, 0), model.INNER
state = ctx.window_manager.btm_wall_editor
chain = s.plan.chains[0]


class Recorder:
    def __init__(self):
        object.__setattr__(self, 'props', [])

    def __getattr__(self, name):
        def call(*args, **kwargs):
            if name == 'prop' and len(args) >= 2:
                self.props.append(args[1])
            return self
        return call

    def __setattr__(self, key, value):
        pass


# 1. Reprodução: o painel mostra a unidade da planta, sem arredondar.
assert (state.length_text, state.thickness_text, state.height_text, state.end_height_text) == \
    ("4000 mm", "150 mm", "2600 mm", "2600 mm"), (state.length_text, state.thickness_text, state.height_text)

# 2. Reprodução: o painel desenha os campos de texto.
rec = Recorder()
panels.BTM_PT_WallEditorSegment.draw(types.SimpleNamespace(layout=rec), ctx)
assert {'length_text', 'thickness_text', 'height_text', 'end_height_text'} <= set(rec.props), rec.props
assert 'length' not in rec.props and 'thickness' not in rec.props, rec.props

# 3. Regressão: digitar na unidade do projeto, ou com sufixo.
state.length_text = "4100"
assert abs(chain.face_length(0, model.INNER) - 4.1) < 1e-9, chain.face_length(0, model.INNER)
state.length_text = "4,2 m"
assert abs(chain.face_length(0, model.INNER) - 4.2) < 1e-9
state.thickness_text = "100"
assert abs(chain.segments[0].thickness - 0.1) < 1e-9

# 4. Regressão: valor inválido mostra o erro e não muda a parede.
state.length_text = "abc"
assert s.error and abs(chain.face_length(0, model.INNER) - 4.2) < 1e-9, s.error

# 5. Regressão: mudar pelo painel é um passo de desfazer (#8).
assert s.undo() and abs(s.plan.chains[0].segments[0].thickness - 0.15) < 1e-9
props.end()
print("blender_bug_VQ72_panel: OK")
