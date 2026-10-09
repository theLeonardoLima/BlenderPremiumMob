"""Baixa as wheels das dependências do leitor de SketchUp (feature 009, T042; D-15).

Uso:
    python3 tools/fetch_wheels.py

Versões fixas, Python 3.13 (o do Blender 5.2), para Linux x86_64 e aarch64, Windows x64 e macOS x86_64 e arm64. As
wheels vão para `caffmob_draw/wheels/` e a lista `wheels = [...]` do `blender_manifest.toml` é reescrita; o Blender
instala na instalação da extensão só as da plataforma dele.

Licenças: openskp (MIT), defusedxml (PSF), mapbox_earcut (ISC), shapely (BSD-3-Clause), compatíveis com a GPL.
"""

import hashlib
import json
import re
import shutil
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WHEELS = ROOT / "caffmob_draw" / "wheels"
MANIFEST = ROOT / "caffmob_draw" / "blender_manifest.toml"

PURE = (("openskp", "1.3.0"), ("defusedxml", "0.7.1"))
BINARY = (("mapbox_earcut", "2.1.0"), ("shapely", "2.2.0"))
# Marcas no nome da wheel (cp313) para Linux x86_64 e aarch64, Windows x64 e macOS x86_64 e arm64
PLATFORMS = ("manylinux_2_28_x86_64", "manylinux_2_28_aarch64", "win_amd64", "macosx_11_0_arm64", "x86_64.whl")


def _files(name, version):
    with urllib.request.urlopen(f"https://pypi.org/pypi/{name}/{version}/json", timeout=60) as resp:
        return json.load(resp)["urls"]


def _fetch(entry):
    target = WHEELS / entry["filename"]
    with urllib.request.urlopen(entry["url"], timeout=120) as resp:
        data = resp.read()
    if hashlib.sha256(data).hexdigest() != entry["digests"]["sha256"]:
        raise RuntimeError(f"SHA-256 não confere: {entry['filename']}")
    target.write_bytes(data)


def download():
    for name, version in PURE:
        files = [f for f in _files(name, version) if f["filename"].endswith("-none-any.whl")]
        _fetch(files[0])
    for name, version in BINARY:
        files = [f for f in _files(name, version) if "-cp313-cp313-" in f["filename"]]
        for mark in PLATFORMS:
            found = [f for f in files if mark in f["filename"] and ("macosx" in f["filename"]) == (
                mark.startswith("macosx") or mark == "x86_64.whl")]
            if not found:
                raise RuntimeError(f"Sem wheel {name} {version} para {mark}")
            _fetch(found[0])


def write_manifest(names):
    text = MANIFEST.read_text(encoding="utf-8")
    block = "wheels = [\n" + "".join(f'    "./wheels/{n}",\n' for n in names) + "]\n"
    if re.search(r"^wheels = \[.*?^\]\n", text, flags=re.S | re.M):
        text = re.sub(r"^wheels = \[.*?^\]\n", block, text, flags=re.S | re.M)
    else:
        text = text.replace("\n[permissions]", "\n" + block + "\n[permissions]", 1)
    MANIFEST.write_text(text, encoding="utf-8")


def main():
    if WHEELS.exists():
        shutil.rmtree(WHEELS)
    WHEELS.mkdir(parents=True)
    download()
    names = sorted(p.name for p in WHEELS.glob("*.whl"))
    write_manifest(names)
    print(f"{len(names)} wheels em {WHEELS}")


if __name__ == "__main__":
    main()
