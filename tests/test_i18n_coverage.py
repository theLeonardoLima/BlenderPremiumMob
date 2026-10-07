"""Cobertura da tradução da interface (BUG-20261007-FLZO).

- Reprodução: nas áreas já entregues, todo texto de interface tem pt_BR e en_US no catálogo e nenhum é montado por
  f-string (texto montado não tem como ser traduzido).
- Regressão: nas demais áreas, só podem faltar os textos da lista de pendências (`fixtures/i18n_pendentes.json`); texto
  novo sem tradução quebra o teste. A lista diminui a cada etapa e acaba vazia.
- O catálogo é válido: as duas línguas preenchidas, os mesmos `{}` do texto original e cada texto num arquivo só.
"""

import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
import i18n_scan as scan  # noqa: E402

# Áreas ainda em tradução: nenhuma (etapas A a F entregues). Área nova entra traduzida.
PENDING_AREAS = []
PENDING = ROOT / "tests" / "fixtures" / "i18n_pendentes.json"
FIELD = re.compile(r"\{[^{}]*\}")      # campos de .format: "{}", "{:.0f}"


def all_areas():
    names = {p.name for p in scan.PACKAGE.iterdir() if p.is_dir() and p.name not in ('__pycache__', 'translations')}
    names |= {p.name for p in scan.PACKAGE.glob('*.py')}
    names.discard('product_libraries')
    names |= {f"product_libraries/{p.name}" for p in (scan.PACKAGE / 'product_libraries').iterdir() if p.is_dir()
              and p.name != '__pycache__'}
    names |= {f"product_libraries/{p.name}" for p in (scan.PACKAGE / 'product_libraries').glob('*.py')}
    return sorted(names)


def other_areas():
    return [a for a in all_areas() if a in PENDING_AREAS]


DONE = [a for a in all_areas() if a not in PENDING_AREAS]


class TestCoverage(unittest.TestCase):
    def setUp(self):
        self.catalog = scan.load_catalog()

    def test_areas_entregues_traduzidas(self):
        absent, dynamic = scan.missing(scan.scan(DONE), self.catalog)
        self.assertEqual([f"{t.path}:{t.line} {t.msgid!r}" for t in absent], [])
        self.assertEqual([f"{t.path}:{t.line} {t.msgid!r}" for t in dynamic], [])

    def test_sem_texto_novo_sem_traducao(self):
        pending = json.loads(PENDING.read_text(encoding='utf-8'))
        allowed = set(pending['textos'])
        allowed_dynamic = set(pending['dinamicos'])
        absent, dynamic = scan.missing(scan.scan(other_areas()), self.catalog)
        self.assertEqual(sorted({t.msgid for t in absent} - allowed), [])
        self.assertEqual(sorted({f"{t.path}|{t.msgid}" for t in dynamic} - allowed_dynamic), [])

    def test_catalogo_valido(self):
        files = sorted(scan.CATALOG.glob('*.json'))
        self.assertTrue(files)
        owner = {}
        for path in files:
            for msgid, entry in json.loads(path.read_text(encoding='utf-8')).items():
                self.assertNotIn(msgid, owner, f"{msgid!r} em {owner.get(msgid)} e em {path.name}")
                owner[msgid] = path.name
                for locale in scan.LOCALES:
                    text = entry.get(locale, '')
                    self.assertTrue(text.strip(), (path.name, msgid, locale))
                    self.assertEqual(FIELD.findall(text), FIELD.findall(msgid), (path.name, msgid, locale))


if __name__ == "__main__":
    unittest.main()
