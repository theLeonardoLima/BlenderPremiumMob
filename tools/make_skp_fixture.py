"""Gera os SketchUp de teste: `tests/fixtures/porta_teste.skp` (feature 009, T046) e `porta_aninhada.skp` (010, T004).

Uso (num Python com o OpenSKP, por exemplo `pip install openskp==1.3.0`):
    python3 tools/make_skp_fixture.py

Porta em polegadas (unidade interna do SketchUp): componente "Batente" (material "Branco") e "Folha" (material
"Madeira", com textura PNG de 8 × 8 px). Instâncias "Batente 1" e "Folha 1". Feita pelo próprio projeto: sem questão
de licença de modelo (RN-09).
"""

import struct
import tempfile
import zlib
from pathlib import Path

import openskp

OUT = Path(__file__).resolve().parents[1] / "tests" / "fixtures" / "porta_teste.skp"
NESTED = OUT.parent / "porta_aninhada.skp"


def png(path, size=8, rgb=(150, 100, 60)):
    raw = b"".join(b"\x00" + bytes(rgb) * size for _ in range(size))

    def chunk(kind, data):
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data) & 0xffffffff)
    data = (b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", struct.pack(">IIBBBBB", size, size, 8, 2, 0, 0, 0))
            + chunk(b"IDAT", zlib.compress(raw)) + chunk(b"IEND", b""))
    Path(path).write_bytes(data)


def box(definition, lo, hi, material):
    (x0, y0, z0), (x1, y1, z1) = lo, hi
    p = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    for face in ((0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)):
        definition.add_face([p[i] for i in face], material=material)


def main():
    with tempfile.TemporaryDirectory() as tmp:
        texture = Path(tmp) / "madeira.png"
        png(texture)
        model = openskp.create()
        white = model.add_material("Branco", (240, 240, 240, 255))
        wood = model.add_texture_material("Madeira", str(texture), applied_width=20.0, applied_height=20.0)
        with model.add_component_definition("Batente") as frame:
            box(frame, (0, 0, 0), (2, 1.5, 82), white)
            box(frame, (32, 0, 0), (34, 1.5, 82), white)
            box(frame, (0, 0, 82), (34, 1.5, 84), white)
        with model.add_component_definition("Folha") as leaf:
            box(leaf, (0, 0, 0), (29.9, 1.4, 81.5), wood)          # cabe entre os montantes (2 a 32)
        model.add_instance(frame, name="Batente 1")
        model.add_instance(leaf, name="Folha 1", translation=(2.05, 0.05, 0.25))
        OUT.parent.mkdir(parents=True, exist_ok=True)
        model.save(str(OUT))
    print(OUT)
    nested()


def nested():
    """Porta 75 × 200 com 3 dobradiças e a maçaneta **dentro** da definição da folha, batente, uma figura de escala
    (`2D_Woman_Standing_Teste`) e o material de camada `Layer_Layer0` (feature 010: RN-07 a RN-09)."""
    model = openskp.create()
    layer = model.add_material("Layer_Layer0", (200, 200, 200, 255))
    metal = model.add_material("Metal", (180, 180, 185, 255))
    with model.add_component_definition("Dobradica") as hinge:
        box(hinge, (0, 0, 0), (0.12, 1.3, 3.5), metal)
    with model.add_component_definition("Macaneta") as handle:
        box(handle, (0, -2.5, 0), (4.5, 0, 0.7), metal)
    with model.add_component_definition("Folha") as leaf:
        box(leaf, (0, 0, 0), (29.0, 1.4, 78.5), layer)
        for z in (8.0, 39.0, 70.0):
            leaf.add_instance(hinge, name="Dobradica", translation=(-0.12, 0.05, z))
        leaf.add_instance(handle, name="Macaneta", translation=(25.0, 0.0, 40.0))
    with model.add_component_definition("Batente") as frame:
        box(frame, (0, 0, 0), (1.5, 1.5, 80), layer)
        box(frame, (30.6, 0, 0), (32.1, 1.5, 80), layer)
        box(frame, (0, 0, 80), (32.1, 1.5, 81.5), layer)
    with model.add_component_definition("2D_Woman_Standing_Teste") as person:
        box(person, (0, 0, 0), (16, 0.1, 66), layer)
    model.add_instance(frame, name="Batente 1")
    model.add_instance(leaf, name="Folha 1", translation=(1.55, 0.05, 0.25))
    model.add_instance(person, name="Pessoa", translation=(40, 0, 0))
    model.save(str(NESTED))
    print(NESTED)


if __name__ == "__main__":
    main()
