---
schema_version: 1
id: BUG-20261007-FLZO
display_number: 11
title: Interface metade em português e metade em inglês
status: resolved
phase: delivering
severity: medium
priority: P2
created: 2026-10-07
updated: 2026-10-07

origin:
  type: manual-report
  external_ref: null

area: interface
module: ui
feature: unclassified
labels: [spec-gap, traducao, i18n]

visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "1/1"
  suspected_triggers: []

blocking: []

relationships:
  - bug: BUG-20261006-QAVK
    type: related-to
    state: proposed
    evidence: []

traceability:
  specs: ["_reversa_sdd/addenda/bug-BUG-20261007-FLZO-v001.md", "_reversa_sdd/addenda/bug-BUG-20261007-FLZO-v002.md", "_reversa_sdd/addenda/bug-BUG-20261006-QAVK-v001.md", "_reversa_sdd/ui/requirements.md"]
  affected_code: ["caffmob_draw/data/i18n.py", "caffmob_draw/ui/", "caffmob_draw/walls2d/", "caffmob_draw/operators/", "caffmob_draw/product_libraries/"]
  root_cause:
    state: confirmed
    hypothesis: "Sem língua-fonte única, catálogo com ~270 de ~4.000 textos e só no contexto '*' (rótulo de operador é traduzido no contexto 'Operator'), e textos montados/desenhados (f-string, barra de status, blf) fora da tradução."
    causal_path:
      - "data/i18n.py: dicionário parcial, só contexto '*'"
      - "sonda: ('Place Door','Operator') sem tradução; entradas en_US valem com o Blender em inglês"
      - "walls2d/ops_editor.py: dica da barra de status desenhada por draw.text sem tradução"
    evidence:
      - ref: evidence/reproduction.md
        observation: "sonda de contextos e levantamento AST (3.975 textos únicos)"
    code_refs:
      - {file: caffmob_draw/data/i18n.py, symbol: translations_dict, commit: b92ac2e}
      - {file: caffmob_draw/walls2d/ops_editor.py, symbol: draw_editor, commit: b92ac2e}
  reproduction_tests: ["tests/blender_bug_FLZO_i18n.py", "tests/test_i18n_coverage.py"]
  regression_tests: ["tests/test_i18n_coverage.py"]

spec_verdict: spec-gap

change_set:
  - id: CHG-001
    kind: code
    artifact: "caffmob_draw/data/i18n.py, caffmob_draw/data/translations/*.json"
    purpose: "etapa A: catálogo JSON por área, tr()/N_(), contextos * e Operator"
    diff: fix/CHG-001-i18n.diff
  - id: CHG-002
    kind: code
    artifact: "caffmob_draw/walls2d/, caffmob_draw/ui/, caffmob_draw/data/units.py, caffmob_draw/canvas2d/draw.py"
    purpose: "etapa A: textos montados e desenhados passam por tr()/N_()"
    diff: fix/CHG-002.diff
  - id: CHG-003
    kind: tooling
    artifact: tools/i18n_scan.py
    purpose: levantamento AST dos textos de interface
    diff: fix/CHG-003.diff
  - id: CHG-004
    kind: test
    artifact: tests/blender_002_smoke.py
    purpose: mensagem de validação aceita nas duas línguas
    diff: fix/CHG-004.diff
  - id: CHG-005
    kind: specification
    artifact: _reversa_sdd/addenda/bug-BUG-20261007-FLZO-v001.md
    purpose: regra de idioma da interface (spec-gap)
    diff: null
  - id: CHG-B01
    kind: code
    artifact: "customize/, aggregates/, move_over/, standards/, inspection/, catalog/, geometry_free/, molding/"
    purpose: "etapa B: tr()/N_() nas mensagens e rótulos; library_io sem decisão pelo texto"
    diff: fix/CHG-B01.diff
  - id: CHG-B02
    kind: code
    artifact: "caffmob_draw/data/i18n.py, caffmob_draw/data/translations/*.json"
    purpose: "etapa B: 8 arquivos de catálogo; campo contexto; tr() com contexto"
    diff: fix/CHG-B02-i18n.diff
  - id: CHG-B03
    kind: tooling
    artifact: tools/i18n_scan.py
    purpose: itens de enum em listas concatenadas e tuple()
    diff: fix/CHG-B03-scanner.diff
  - id: CHG-B04
    kind: test
    artifact: "tests/_blender_env.py, tests/test_i18n_coverage.py, tests/blender_bug_FLZO_i18n.py"
    purpose: "áreas da etapa B na cobertura; smokes em pt_BR"
    diff: fix/CHG-B04-testes.diff
  - id: CHG-B05
    kind: specification
    artifact: _reversa_sdd/addenda/bug-BUG-20261007-FLZO-v002.md
    purpose: contexto de tradução próprio e regra de mensagens
    diff: null
  - id: CHG-C01
    kind: code
    artifact: "operators/, arquivos da raiz, cutting/, selection/, measure/"
    purpose: "etapa C: tr()/N_() em mensagens, cabeçalhos e rótulos; draw_header_text traduz"
    diff: fix/CHG-C01.diff
  - id: CHG-C02
    kind: code
    artifact: "aggregates/ops_aggregate.py, inspection/ops_inspect.py, move_over/insertion_plane.py, move_over/ops_dialog.py"
    purpose: "constantes cruas no cabeçalho (etapa B) passam por tr()"
    diff: fix/CHG-C02-etapaB-cabecalhos.diff
  - id: CHG-C03
    kind: tooling
    artifact: tools/i18n_scan.py
    purpose: "pendência 'cru' para header_text_set/status_text_set/blf.draw; enum em append e return"
    diff: fix/CHG-C03-scanner.diff
  - id: CHG-C04
    kind: test
    artifact: "tests/test_i18n_coverage.py, tests/blender_bug_FLZO_i18n.py"
    purpose: "cobertura por áreas pendentes; rótulo de operador herdado"
    diff: fix/CHG-C04-testes.diff
  - id: CHG-D01
    kind: code
    artifact: "product_libraries/closets/, product_libraries/common/"
    purpose: "etapa D: tr()/N_() em mensagens, dicas e rótulos; pílulas do overlay traduzidas"
    diff: fix/CHG-D01.diff
  - id: CHG-D02
    kind: tooling
    artifact: tools/i18n_scan.py
    purpose: "enums em `items or [...]`"
    diff: fix/CHG-D02-scanner.diff
  - id: CHG-D03
    kind: test
    artifact: "tests/test_i18n_coverage.py, tests/blender_bug_FLZO_i18n.py"
    purpose: "closets e common entregues; rótulo de operador do closets"
    diff: fix/CHG-D03-testes.diff
  - id: CHG-E01
    kind: code
    artifact: "product_libraries/frameless/"
    purpose: "etapa E: tr()/N_() em mensagens, cabeçalhos, nomes da biblioteca e rótulos"
    diff: fix/CHG-E01.diff
  - id: CHG-E02
    kind: tooling
    artifact: tools/i18n_scan.py
    purpose: "enums em ternário; ignora expressões de driver em tuplas"
    diff: fix/CHG-E02-scanner.diff
  - id: CHG-E03
    kind: test
    artifact: "tests/test_i18n_coverage.py, tests/blender_bug_FLZO_i18n.py"
    purpose: "frameless entregue; rótulo de operador do frameless"
    diff: fix/CHG-E03-testes.diff
  - id: CHG-F01
    kind: code
    artifact: "product_libraries/face_frame/"
    purpose: "etapa F: tr()/N_() em mensagens, cabeçalhos, menus, padrões de compartimento e biblioteca"
    diff: fix/CHG-F01.diff
  - id: CHG-F02
    kind: tooling
    artifact: tools/i18n_scan.py
    purpose: "versão final do levantamento"
    diff: fix/CHG-F02-scanner.diff
  - id: CHG-F03
    kind: test
    artifact: "tests/test_i18n_coverage.py, tests/blender_bug_FLZO_i18n.py, tests/fixtures/i18n_pendentes.json"
    purpose: "nenhuma área pendente; lista de pendências vazia"
    diff: fix/CHG-F03-testes.diff

closure:
  policy: local-software
  satisfied: true
resolution_kind: fixed
---
# Interface metade em português e metade em inglês

## Summary

A interface do CAFFMob Draw mistura português e inglês. Com o Blender em inglês, os painéis do editor de paredes saem
em inglês, mas a barra de status, os rótulos da planta e diálogos ficam em português; com o Blender em português, os
textos herdados do Home Builder continuam em inglês. O titular pede tradução 100% para en_US e pt_BR.

## Expected Behavior

**spec-gap:** não há especificação de idioma da interface. O adendo de identidade (`bug-BUG-20261006-QAVK-v001`) trata
do nome; o `CLAUDE.md` pede textos novos em português. Pedido do titular (2026-10-07): todos os textos visíveis do
plugin (painéis, menus, operadores, mensagens, barra de status, textos desenhados na viewport e na planta, diálogos)
aparecem inteiramente em inglês com o Blender em en_US e inteiramente em português com o Blender em pt_BR.

## Actual Behavior

- Blender em en_US: painel "Panel"/"Length"/"Tools" em inglês; barra de status "Clique numa face (interna tracejada /
  externa)..." e diálogo "Paredes de outra camada" em português (`evidence/editor-ingles-com-textos-em-portugues.png`).
- `data/i18n.py` cobre ~273 textos; o pacote tem centenas de rótulos herdados em inglês sem entrada `pt_BR` e textos
  desenhados (`blf`, `status_text_set`, `report`) que não passam pela tradução (ver relato).

## Steps to Reproduce

1. Blender em en_US (Preferências › Interface › Tradução): abrir o Editor de Paredes; ver a barra de status em português.
2. Blender em pt_BR: abrir os painéis do CAFFMob Draw e das bibliotecas (frameless, face frame, closets); ver os
   rótulos herdados em inglês.

## Evidence

- `evidence/editor-ingles-com-textos-em-portugues.png`
- Relato: `../../intake/relato-20261007-2030.md`

## Suspected Area

- `data/i18n.py`: dicionário parcial; textos de origem em dois idiomas (sem uma língua-fonte única).
- Textos desenhados por `blf`, `status_text_set`, `self.report` e `layout.label(text=...)` montados com f-string não usam
  `bpy.app.translations.pgettext`.
- Bibliotecas herdadas (`product_libraries/`, `operators/`) com `bl_label`/`description` em inglês.

## Acceptance Criteria

- Com o Blender em en_US, nenhum texto visível do plugin em português; com pt_BR, nenhum em inglês (exceto nomes
  próprios, unidades e nomes de arquivo).
- Um teste automatizado lista os textos sem tradução (e falha se surgir texto novo sem tradução).
- Trocar o idioma do Blender atualiza a interface sem reinstalar o plugin.

## Traceability

- Specs: `_reversa_sdd/addenda/bug-BUG-20261006-QAVK-v001.md` (identidade), `_reversa_sdd/ui/requirements.md`; spec-gap
  para o idioma.
- Código afetado: `data/i18n.py`, `ui/`, `walls2d/`, `operators/`, `product_libraries/`.

## Resolution

**Entregue por etapas** (plano `fix/plan.html`, aprovado em 2026-10-07); as seis etapas passaram pelos dois gates e a
etapa F zerou `tests/fixtures/i18n_pendentes.json`. Resultado: 5.678 textos únicos de interface no pacote, nenhum sem
tradução e nenhum montado fora de `tr()`; catálogo em 29 arquivos de `caffmob_draw/data/translations/`.

**Causa raiz (confirmed):** sem língua-fonte única; catálogo com ~270 de ~4.000 textos e só no contexto `*` (o
Blender traduz `bl_label` de operador no contexto `Operator`); textos montados e desenhados fora da tradução.

**Veredito de spec:** `spec-gap`, adendos `_reversa_sdd/addenda/bug-BUG-20261007-FLZO-v001.md` e `-v002.md`.

| etapa | áreas | estado |
|---|---|---|
| A | infra, `walls2d/`, `ui/`, `data/`, `canvas2d/` | entregue 2026-10-07 (CHG-001 a CHG-005) |
| B | customize, aggregates, move_over, standards, inspection, catalog, geometry_free, molding | entregue 2026-10-07 (CHG-B01 a CHG-B05) |
| C | `operators/`, raiz do pacote, `cutting/`, `selection/`, `measure/` | entregue 2026-10-07 (CHG-C01 a CHG-C04) |
| D | closets + common | entregue 2026-10-07 (CHG-D01 a CHG-D03) |
| E | frameless | entregue 2026-10-07 (CHG-E01 a CHG-E03) |
| F | face frame | entregue 2026-10-07 (CHG-F01 a CHG-F03) |

**Testes da etapa A (vermelho → verde):** `test_i18n_coverage` (578 sem tradução e 32 dinâmicos → 0 e 0);
`blender_bug_FLZO_i18n` (en_US: dica do editor ficava em português → em inglês; pt_BR: "Wall Thickness" traduzido nos
contextos * e Operator; troca de idioma ao vivo). Smokes do Blender (16), 170 testes unitários, ruff e check_api verdes.
Pendências restantes depois da etapa A: 3.989 textos e 329 dinâmicos.

**Etapa B:** cobertura das 8 áreas 245 sem tradução e 36 dinâmicos → 0 e 0 (o scanner passou a ver mais itens de enum: 555 entradas no fim); `blender_bug_FLZO_i18n` com "Empilhar" → "Stack" em en_US; 16 testes no Blender, 170 unitários, ruff e check_api verdes. Pendências restantes: 3.731 textos e 293 dinâmicos.

**Etapa C:** cobertura fora das bibliotecas: cerca de 1.044 sem tradução e 98 dinâmicos → 0 e 0; `blender_bug_FLZO_i18n` com "Place Door" → "Inserir Porta" (contexto Operator) em pt_BR. O scanner passou a cobrar `tr()` em constante passada direto a `header_text_set`, `status_text_set` e `blf.draw` (não traduzem): 9 casos corrigidos, 4 deles de áreas da etapa B. 16 testes no Blender, 170 unitários, ruff e check_api verdes. Pendências restantes (só bibliotecas): 2.949 textos e 201 dinâmicos.

**Etapa D:** closets e common: 392 sem tradução e 23 dinâmicos → 0 e 0 (480 entradas no fim, com os enums que o scanner passou a ver); `blender_bug_FLZO_i18n` com "Reset Closet Dimension Label" traduzido em pt_BR. 16 testes no Blender, 170 unitários, ruff e check_api verdes. Pendências restantes (frameless e face frame): 2.549 textos e 179 dinâmicos.

**Etapa E:** frameless: 1.057 sem tradução e 79 dinâmicos → 0 e 0 (1.152 entradas no fim); `blender_bug_FLZO_i18n` com "Add Countertops" traduzido em pt_BR. Nenhum `tr()` roda ao carregar o add-on (conferido pela AST). 16 testes no Blender, 170 unitários, ruff e check_api verdes. Pendências restantes (só face frame): 1.485 textos e 106 dinâmicos.

**Etapa F:** face frame: 1.485 sem tradução e 124 dinâmicos → 0 e 0 (1.670 entradas no fim); `blender_bug_FLZO_i18n` com "Join Cabinets" traduzido em pt_BR. Pacote inteiro: 0 pendências. 16 testes no Blender, 170 unitários, ruff e check_api verdes.

## Agent Notes

- Severidade/prioridade escolhidas pelo titular em 2026-10-07 (medium/P2).
- Em 2026-10-07 (relato 1500) o titular tinha preferido tratar como feature; agora pediu registro como bug. Escopo grande
  (o add-on inteiro): o fix deve propor etapas (ex.: escolher a língua-fonte, extrair os textos, dicionário completo,
  `pgettext` nos textos desenhados, teste de cobertura) e entregar por área.
- Etapa A: o botão de vão livre passou de "Open" para "Open Passage" ("Open" colidiria com o Abrir do Blender).
- Etapa B: itens do catálogo de produtos traduzidos no contexto `caffmob_catalogo` (o nome é o id; "Range" colidiria com o Blender). Nomes de dados (definições embutidas "Padrão Brasil", nomes de peças de geometria livre, perfis de moldura) ficaram fora: são dados, não interface.
- Etapa C: ficaram fora nomes de dados ("Room {}", "Cut - {}", "Floor.{}", "Crown - {}", "{} CLG.") e erros de programação ("Subclass must implement…", "Input '{}' not found…").
- Etapa D: as propriedades "Bay 1..N" da coifa de madeira passaram a "Bay" com dica fixa (o nome não aparece no painel, `text=""`; o número segue no rótulo). Nomes de peças, acabamentos de catálogo de fornecedor e sockets ficaram fora.
- Etapa E: nomes de prompt e de socket do modelo (`types_frameless.py`, `types_products.py`), cores de fornecedor, parâmetros de shader e textos que vão para a prancha ("BASE ({})") ficaram fora: são dados.
- Etapa F: `style_options.py` (catálogo do fornecedor CWP gerado de planilha: séries, espécies, cores, vernizes, códigos) ficou fora da tradução por ser dado de fornecedor, decisão aprovada no gate 2. Nomes de peças do solver e sockets também.
- Durante a etapa F o script de conversão sobrepôs edições numa f-string com formato (`{x:.1f}`) e quebrou `ops_placement.py`; o arquivo foi restaurado do git e reconvertido, e todo o pacote foi conferido por `ast.parse` (as etapas anteriores não tinham resíduo).
- Proposta de taxonomia: `feature: i18n` (não existe em `taxonomy.yaml`).
