"""Leitor de SketchUp pelo OpenSKP (feature 009, T016; RN-13, D-15).

O `openskp` e as dependências dele (`defusedxml`, `mapbox_earcut`, `shapely`) entram como wheels da extensão
(`blender_manifest.toml`). O import é tardio: sem a wheel da plataforma, só a leitura de `.skp` fica indisponível,
com o motivo, e o resto do plugin funciona.
"""

from ..data.i18n import tr


def available():
    """None se dá para ler `.skp`; senão o motivo em texto."""
    try:
        import openskp  # noqa: F401
    except ImportError as exc:
        return tr("leitor de SketchUp indisponível nesta instalação ({})").format(exc.name or exc)
    return None


def read(path):
    """(SkpModel, Scene) do arquivo, ou levanta `ValueError` com o motivo em texto."""
    reason = available()
    if reason:
        raise ValueError(reason)
    import openskp
    try:
        skp = openskp.SkpFile(path)
        model = skp.parse()
        scene = skp.build_scene()
    except FileNotFoundError:
        raise ValueError(tr("arquivo não encontrado")) from None
    except Exception as exc:                 # SkpParseError e falhas do formato: o motivo vai para o usuário
        raise ValueError(str(exc) or type(exc).__name__) from exc
    if not scene.glb_primitives:
        raise ValueError(tr("o arquivo não tem geometria"))
    return model, scene
