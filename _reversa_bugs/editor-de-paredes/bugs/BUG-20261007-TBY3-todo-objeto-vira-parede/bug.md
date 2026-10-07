---
schema_version: 1
id: BUG-20261007-TBY3
display_number: 10
title: Todo objeto é tratado como parede (object_kind padrão WALL)
status: resolved
phase: delivering
severity: medium
priority: P2
created: 2026-10-07
updated: 2026-10-07

origin:
  type: inspection
  external_ref: null

area: paredes
module: wall_editor
feature: 002-editor-parede-mover-sobre
labels: [identificacao-de-parede]

change_risk:
  classification: média
  reasons: ["muda a classificação de objetos sem marcação (passam de Parede para Outro) no painel de Propriedades, no Mover Sobre e nos overlays", "sem migração de dados: arquivos salvos com o tipo gravado continuam iguais", "reversível"]

visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "1/1"
  suspected_triggers: []

blocking: []

relationships:
  - bug: BUG-20261007-A2G7
    type: related-to
    state: supported
    evidence:
      - ref: ../BUG-20261007-A2G7-ajustar-piso-ignora-paredes/bug.md
        observation: "a mesma causa (object_kind padrão 'WALL') fazia o Ajustar Piso tomar qualquer objeto por parede; corrigido lá só no floor_builder"

traceability:
  specs: ["_reversa_forward/002-editor-parede-mover-sobre/requirements.md#RF-02", "_reversa_forward/002-editor-parede-mover-sobre/requirements.md#RF-38", "_reversa_sdd/data/requirements.md"]
  affected_code: ["caffmob_draw/data/properties.py", "caffmob_draw/selection/classify.py", "caffmob_draw/walls2d/scene_io.py", "caffmob_draw/ui/panels.py", "caffmob_draw/operators/opening_builder.py", "caffmob_draw/overlays/draw_handlers.py"]
  root_cause:
    state: confirmed
    hypothesis: "btm_plane.object_kind tem padrão 'WALL' em todo Object e o código compara o valor sem distinguir o padrão de um valor gravado de propósito; qualquer objeto sem marcação passa por parede da camada nova."
    causal_path:
      - "data/properties.py: EnumProperty object_kind com default='WALL' em bpy.types.Object.btm_plane"
      - "selection/classify.py:112, walls2d/scene_io.py:104, operators/opening_builder.py:50,59, overlays/draw_handlers.py:182,233 comparam object_kind == 'WALL'"
      - "no cubo padrão: object_kind == 'WALL' e is_property_set('object_kind') == False"
    evidence:
      - ref: evidence/reproduction.md
        observation: "cubo padrão classificado como Parede BTM, aceito como parede da outra camada e habilitando insert_opening; is_property_set distingue o padrão do valor gravado"
    code_refs:
      - {file: caffmob_draw/data/properties.py, symbol: "BTM_PG_InsertionPlane.object_kind (Object.btm_plane)", commit: 499068f}
      - {file: caffmob_draw/selection/classify.py, symbol: _btm_kind, commit: 499068f}
  reproduction_tests: ["tests/blender_bug_TBY3_walls.py#1"]
  regression_tests: ["tests/blender_bug_TBY3_walls.py#2", "tests/blender_bug_TBY3_walls.py#3"]

spec_verdict: spec-correta

change_set:
  - id: CHG-001
    kind: code
    artifact: caffmob_draw/selection/classify.py
    purpose: btm_kind só com tipo gravado; classificador
    diff: fix/CHG-001.diff
  - id: CHG-002
    kind: code
    artifact: caffmob_draw/walls2d/scene_io.py
    purpose: is_other_layer_wall usa btm_kind
    diff: fix/CHG-002.diff
  - id: CHG-003
    kind: code
    artifact: caffmob_draw/operators/opening_builder.py
    purpose: poll e lista de paredes usam btm_kind
    diff: fix/CHG-003.diff
  - id: CHG-004
    kind: code
    artifact: caffmob_draw/overlays/draw_handlers.py
    purpose: destaque do plano e cotas de parede usam btm_kind
    diff: fix/CHG-004.diff
  - id: CHG-005
    kind: code
    artifact: caffmob_draw/ui/panels.py
    purpose: _scene_has_walls usa btm_kind
    diff: fix/CHG-005.diff

closure:
  policy: local-software
  satisfied: true
resolution_kind: fixed
---
# Todo objeto é tratado como parede (object_kind padrão WALL)

## Summary

`btm_plane.object_kind` (`data/properties.py`, registrado em todo `Object`) tem padrão `'WALL'`. Qualquer objeto sem
marcação (o cubo padrão, módulos, luzes de malha) passa por parede nos lugares que usam esse campo. Ao abrir o Editor
de Paredes num arquivo novo, o cubo vira "parede da outra camada": aparece a pergunta "Converter / Só referência" e o
contorno tracejado dele na planta.

## Expected Behavior

Spec efetiva: `_reversa_forward/002-editor-parede-mover-sobre/requirements.md` RF-02 e RF-38: só as paredes da camada
nova (`caffmob.wall_builder`, com `btm_wall_segments`) aparecem como referência e podem ser convertidas. Objetos que não
são parede não devem aparecer na planta nem disparar a pergunta; o painel só deve considerar paredes reais; o operador de
aberturas da camada nova só deve aceitar paredes reais.

## Actual Behavior

Blender do titular (2026-10-07, arquivo novo com o cubo padrão): `scene_io.is_other_layer_wall(Cube)` é verdadeiro; o
editor pergunta "Converter / Só referência" e desenha o cubo tracejado (`evidence/cubo-como-parede-na-planta.png`).

## Steps to Reproduce

1. Arquivo novo (com o cubo padrão).
2. Abrir o Editor de Paredes: aparece a pergunta "Converter / Só referência".
3. Escolher "Só referência": o contorno do cubo aparece tracejado na planta.

## Evidence

- `evidence/reproduction.md` e `evidence/reproducao.py` (cubo padrão como parede em 4 lugares)
- `evidence/cubo-como-parede-na-planta.png` (quadrado tracejado à esquerda, embaixo, é o cubo)
- Relato: `../../intake/relato-20261007-1800.md`
- Reprodução: `../BUG-20261007-VQ72-medida-do-trecho-no-painel/evidence/reproduction.md` (achado lateral)

## Suspected Area

- `data/properties.py:184-193`: enum `object_kind` com `default='WALL'` (sem valor "nenhum").
- `walls2d/scene_io.py:98-104` `is_other_layer_wall`: malha sem `IS_WALL_BP` com `object_kind == 'WALL'`.
- `ui/panels.py:16` `_scene_has_walls`; `operators/opening_builder.py:50,59` (poll e lista de paredes).
- Referência de correção: `operators/floor_builder.scene_walls` (BUG-20261007-A2G7) reconhece paredes da camada nova por
  `btm_wall_segments`.

## Acceptance Criteria

- Arquivo novo com o cubo padrão: abrir o editor não pergunta nada e a planta não mostra o cubo.
- Paredes da camada nova (com `btm_wall_segments`) continuam aparecendo como referência e podendo ser convertidas.
- `_scene_has_walls` e o operador de aberturas da camada nova só contam paredes reais.
- Arquivos já salvos continuam abrindo (sem migração destrutiva do campo).

## Traceability

- Specs: 002 RF-02, RF-38; `_reversa_sdd/data/requirements.md`
- Código afetado: `data/properties.py`, `walls2d/scene_io.py`, `ui/panels.py`, `operators/opening_builder.py`
- Testes existentes relacionados: `tests/test_walls2d_convert.py`, `tests/blender_002_smoke.py`

## Resolution

**Causa raiz (confirmed):** `btm_plane.object_kind` tem padrão `'WALL'` em todo objeto e o código comparava o valor sem
distinguir o padrão de um valor gravado; qualquer objeto sem marcação passava por parede da camada nova.

**Correção:** `classify.btm_kind(obj)` lê o tipo só quando foi gravado (`is_property_set('object_kind')`); classificador,
editor 2D, inserir abertura, overlays e painel usam essa leitura. Sem mudar o padrão do enum nem migrar arquivos.

**Veredito de spec:** `spec-correta` (aprovado por Leonardo Lima em 2026-10-07): a 002 (RF-02, RF-38) já definia que só
as paredes da camada nova aparecem como referência e podem ser convertidas. Sem adendo.

**resolution_kind:** `fixed`

| CHG | tipo | artefato | propósito |
|---|---|---|---|
| CHG-001 | code | `caffmob_draw/selection/classify.py` | btm_kind só com tipo gravado; classificador |
| CHG-002 | code | `caffmob_draw/walls2d/scene_io.py` | is_other_layer_wall usa btm_kind |
| CHG-003 | code | `caffmob_draw/operators/opening_builder.py` | poll e lista de paredes usam btm_kind |
| CHG-004 | code | `caffmob_draw/overlays/draw_handlers.py` | destaque do plano e cotas de parede usam btm_kind |
| CHG-005 | code | `caffmob_draw/ui/panels.py` | _scene_has_walls usa btm_kind |

**Testes (vermelho → verde):**
- Antes: `tests/blender_bug_TBY3_walls.py` → `AssertionError: Classified(kind='WALL', obj=Cube, root=Cube, library='BTM')`.
- Depois: `blender_bug_TBY3_walls: OK` (3 casos); suíte unitária; `blender_002_smoke`, `blender_bug_A2G7_floor`,
  `blender_003_move_over_smoke`, `blender_bug_VQ72_panel` e `blender_002_ui_events` (13 casos) OK; `ruff` e
  `check_api.py` limpos.

## Agent Notes

- Severidade/prioridade escolhidas pelo titular em 2026-10-07 (medium/P2).
- Preferir reconhecer paredes por marca real (`IS_WALL_BP`, `btm_wall_segments`) a mudar o padrão do enum: mudar o padrão
  afeta arquivos salvos (objetos sem valor gravado passariam a ler o novo padrão).
