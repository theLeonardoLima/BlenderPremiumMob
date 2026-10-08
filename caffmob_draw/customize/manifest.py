"""Manifesto do módulo salvo pelo usuário (feature 003, T002; D-10). Python puro, sem `bpy`.

Contrato: `_reversa_forward/003-modulos-agregados-reposicionar/interfaces/user-module-file.md`; a 1.1.0 (feature 006)
acrescenta `structure` e `divisions`, opcionais: `_reversa_forward/006-editor-armario-abas/interfaces/user-module-file.md`.
"""

import json
import re

from ..data.i18n import tr
from . import spec as spec_mod

FORMAT = "caffmob_draw.user-module"
SCHEMA_VERSION = "1.1.0"
SUPPORTED_MAJOR = 1
LIBRARIES = ('FRAMELESS', 'FACE_FRAME', 'CLOSETS', 'BTM')
ROLES = ('TOP', 'BOTTOM', 'BACK', 'LEFT', 'RIGHT')
MODES = ('KEEP', 'EXTEND', 'SHRINK')
ORIENTATIONS = ('VERTICAL', 'HORIZONTAL')
_SPACE = re.compile(r'^s\d+(\.[ab])*$')
_FORBIDDEN = re.compile(r'[<>:"/\\|?*\x00-\x1f]')


def file_stem(name):
    """Nome de arquivo seguro em Windows/Linux; o nome original fica no manifesto."""
    stem = _FORBIDDEN.sub("_", str(name)).strip().rstrip(".")
    return stem or "modulo"


def build(name, category, library, root_object, spec, *, created="", addon_version="", dimensions_mm=None,
          styles=None, materials=(), pulls=(), structure=None, divisions=None):
    data = {
        "format": FORMAT,
        "schema_version": SCHEMA_VERSION,
        "name": str(name),
        "category": str(category),
        "library": str(library),
        "root_object": str(root_object),
        "created": str(created),
        "addon_version": str(addon_version),
        "dimensions_mm": dict(dimensions_mm or {}),
        "styles": dict(styles or {}),
        "materials": sorted({str(m) for m in materials if m}),
        "pulls": sorted({str(p) for p in pulls if p and p != spec_mod.NO_PULL}),
        "spec": spec_mod.to_dict(spec),
    }
    if structure:
        data["structure"] = {role: {"removed": bool(v.get("removed")), "mode": v.get("mode") or 'KEEP',
                                    "thickness_mm": _mm(v.get("thickness")), "material": str(v.get("material") or "")}
                             for role, v in sorted(structure.items())}
    if divisions:
        data["divisions"] = [{"uid": str(d.get("uid", "")), "space": d["space"], "orientation": d["orientation"],
                              "offset_mm": _mm(d.get("offset")), "use_front": bool(d.get("use_front")),
                              "front_mm": _mm(d.get("front")), "use_back": bool(d.get("use_back")),
                              "back_mm": _mm(d.get("back")), "thickness_mm": _mm(d.get("thickness")),
                              "material": str(d.get("material") or "")} for d in divisions]
    return data


def _mm(value):
    return round(float(value or 0.0) * 1000.0, 3)


def _m(value):
    return float(value or 0.0) / 1000.0


def structure_of(data):
    """Estrutura do manifesto em metros: {papel: {removed, mode, thickness, material}} (vazio na 1.0.0)."""
    return {role: {"removed": bool(v.get("removed")), "mode": v.get("mode") or 'KEEP',
                   "thickness": _m(v.get("thickness_mm")), "material": str(v.get("material") or "")}
            for role, v in (data.get("structure") or {}).items()}


def divisions_of(data):
    """Divisões do manifesto em metros (vazio na 1.0.0)."""
    return [{"uid": str(d.get("uid", "")), "space": d["space"], "orientation": d["orientation"],
             "offset": _m(d.get("offset_mm")), "use_front": bool(d.get("use_front")), "front": _m(d.get("front_mm")),
             "use_back": bool(d.get("use_back")), "back": _m(d.get("back_mm")),
             "thickness": _m(d.get("thickness_mm")), "material": str(d.get("material") or "")}
            for d in (data.get("divisions") or [])]


def _negative(entry, keys):
    return any(float(entry.get(k) or 0.0) < 0.0 for k in keys)


def _validate_structure(data):
    errors = []
    for role, entry in (data.get("structure") or {}).items():
        if role not in ROLES:
            errors.append(tr("componente desconhecido: {!r}").format(role))
            continue
        if entry.get("mode", 'KEEP') not in MODES:
            errors.append(tr("modo desconhecido: {!r}").format(entry.get("mode")))
        if _negative(entry, ("thickness_mm",)):
            errors.append(tr("medida negativa em {}").format(role))
    for entry in data.get("divisions") or []:
        if not _SPACE.match(str(entry.get("space", ""))):
            errors.append(tr("vão mal formado: {!r}").format(entry.get("space")))
        if entry.get("orientation") not in ORIENTATIONS:
            errors.append(tr("orientação desconhecida: {!r}").format(entry.get("orientation")))
        if _negative(entry, ("offset_mm", "front_mm", "back_mm", "thickness_mm")):
            errors.append(tr("medida negativa numa divisão"))
    return errors


def _major(version):
    try:
        return int(str(version).split(".")[0])
    except ValueError:
        return None


def validate(data):
    errors = []
    if not isinstance(data, dict):
        return [tr("o manifesto não é um objeto JSON")]
    if data.get("format") != FORMAT:
        errors.append(tr("formato desconhecido: {!r}").format(data.get('format')))
    major = _major(data.get("schema_version", ""))
    if major is None or major > SUPPORTED_MAJOR:
        errors.append(tr("schema_version {!r} não suportada (máximo {}.x)").format(data.get('schema_version'), SUPPORTED_MAJOR))
    if data.get("library") not in LIBRARIES:
        errors.append(tr("biblioteca desconhecida: {!r}").format(data.get('library')))
    if not str(data.get("name", "")).strip():
        errors.append(tr("nome vazio"))
    if not str(data.get("root_object", "")).strip():
        errors.append(tr("objeto raiz não informado"))
    if not errors:
        errors += spec_mod.validate(spec_mod.from_dict(data.get("spec")))
        errors += _validate_structure(data)
    return errors


def dumps(data):
    return json.dumps(data, ensure_ascii=False, indent=2, sort_keys=False) + "\n"


def loads(text):
    """Lê e valida; devolve (dados, spec, erros). Com erro, `spec` é None."""
    try:
        data = json.loads(text)
    except ValueError as exc:
        return None, None, [tr("JSON inválido: {}").format(exc)]
    errors = validate(data)
    if errors:
        return data, None, errors
    return data, spec_mod.from_dict(data.get("spec")), []
