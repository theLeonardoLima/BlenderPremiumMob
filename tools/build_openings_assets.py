"""Converte as texturas de nogueira da porta realista para o pacote (feature 010, T002; D-09).

Uso:
    blender --background --factory-startup --python tools/build_openings_assets.py

Origem: `docs/porta_realista_080x210/nogueira_cor.png` e `nogueira_rugosidade.png` (1024 × 2048), geradas pelo
`gerar_porta.py` daquela pasta (modelo original do projeto). Os PNG não são versionados: num clone, rode o gerador
antes. Saída: `caffmob_draw/openings/assets/nogueira_*.jpg` (JPEG 88), compartilhadas por todas as portas do arquivo.
"""

from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "docs" / "porta_realista_080x210"
OUT = ROOT / "caffmob_draw" / "openings" / "assets"


def convert(name):
    image = bpy.data.images.load(str(SOURCE / (name + ".png")))
    scene = bpy.context.scene
    scene.render.image_settings.file_format = 'JPEG'
    scene.render.image_settings.quality = 88
    scene.render.image_settings.color_mode = 'RGB'
    target = OUT / (name + ".jpg")
    image.save_render(str(target), scene=scene)
    print(target, target.stat().st_size)


OUT.mkdir(parents=True, exist_ok=True)
for texture in ("nogueira_cor", "nogueira_rugosidade"):
    convert(texture)
