---
schema_version: 1
id: BUG-20261006-KFAR
display_number: 4
title: Erro ao salvar no Windows com o editor de paredes e o construtor de paredes
status: resolved
phase: delivering
severity: critical
priority: P0
created: 2026-10-06
updated: 2026-10-07

origin:
  type: manual-report
  external_ref: null

area: paredes
module: wall_editor
feature: 002-editor-parede-mover-sobre
labels: [windows, ambiente, empacotamento]

change_risk:
  classification: baixa
  reasons: ["só repositório e empacotamento; o código do plugin não muda", "os .blend versionados são idênticos aos da raiz (o git guarda uma vez)", "reversível"]

visibility: normal
security_suspected: false

reproduction:
  classification: deterministic
  rate: "1/1 (pacote gerado de um clone limpo do GitHub, master b92ac2e)"
  suspected_triggers: ["OK do editor de paredes cria GeoNodeWall a partir de caffmob_draw/geometry_nodes/GeoNodeWall.blend", "plugin montado a partir de um clone do GitHub (os .blend do pacote não estão no git)"]

blocking: []

relationships: 
  - bug: BUG-20261006-SCVF
    type: caused-by
    state: rejected
    evidence:
      - ref: ../../../plugin-caffmob-draw/bugs/BUG-20261006-SCVF-copia-antiga-na-raiz-e-addon-legado/evidence/reproduction.md
        observation: "a cópia antiga da raiz não registra (sem ui/), então não pode rodar junto da extensão; com só a extensão nova, salvar funciona" 

traceability:
  specs: ["_reversa_forward/002-editor-parede-mover-sobre/requirements.md#RN-16", "_reversa_sdd/addenda/bug-BUG-20261006-KFAR-v001.md", "_reversa_sdd/wall_editor/requirements.md"]
  affected_code: ["blendertomob/walls2d/ops_editor.py", "blendertomob/walls2d/window.py", "blendertomob/inspection/save_guard.py", "blendertomob/operators/walls.py"]
  root_cause:
    state: confirmed
    hypothesis: "O .gitignore ignora *.blend, então os 107 arquivos .blend do pacote caffmob_draw/ (nós de Geometry Nodes, modificadores de peça, puxadores, perfis, materiais) nunca foram para o GitHub. Quem gera o plugin a partir de um clone (o titular, no Windows) recebe um pacote sem eles, e criar parede (GeoNodeWall.create → bpy.data.libraries.load) falha."
    causal_path:
      - ".gitignore: *.blend (sem exceção para o pacote)"
      - "git ls-files caffmob_draw: nenhum .blend; só os da cópia antiga na raiz estão versionados"
      - "build.py empacota só o que existe no disco, sem conferir os arquivos de que o código precisa"
      - "hb_types.py:59 GeoNodeObject.create → bpy.data.libraries.load(geometry_nodes/GeoNodeWall.blend) → OSError"
    evidence:
      - ref: evidence/reproduction.md
        observation: "clone limpo do master + build.py → zip com 0 de 107 .blend; criar paredes dá o mesmo OSError do print do titular"
    code_refs:
      - {file: .gitignore, symbol: "*.blend", commit: b92ac2e}
      - {file: build.py, symbol: build_zip, commit: b92ac2e}
      - {file: caffmob_draw/hb_types.py, symbol: GeoNodeObject.create, commit: b92ac2e}
  reproduction_tests: ["tests/test_packaging.py::test_blends_do_pacote_estao_no_git"]
  regression_tests: ["tests/test_packaging.py::test_build_recusa_pacote_sem_blend", "tests/test_packaging.py::test_zip_tem_manifesto_na_raiz"]

spec_verdict: spec-gap

change_set:
  - id: CHG-001
    kind: configuration
    artifact: .gitignore
    purpose: exceção !caffmob_draw/**/*.blend
    diff: fix/CHG-001.diff
  - id: CHG-002
    kind: code
    artifact: build.py
    purpose: recusa pacote sem os .blend de nós usados no código
    diff: fix/CHG-002.diff
  - id: CHG-003
    kind: other
    artifact: caffmob_draw/**/*.blend (107 arquivos)
    purpose: passam a ser rastreados pelo git
    diff: fix/CHG-003-arquivos.txt
  - id: CHG-004
    kind: documentation
    artifact: CLAUDE.md
    purpose: regra de versionamento dos .blend do pacote
    diff: fix/CHG-004.diff
  - id: CHG-005
    kind: specification
    artifact: _reversa_sdd/addenda/bug-BUG-20261006-KFAR-v001.md
    purpose: adendo aditivo (spec-gap)
    diff: null

closure:
  policy: local-software
  satisfied: true
resolution_kind: fixed
---
# Erro ao salvar no Windows com o editor de paredes e o construtor de paredes

## Summary

Num computador com Windows (Blender 5.2.0, Home Builder "vindo junto na instalação"), abrir o editor de paredes e
salvar retorna erro; o construtor de paredes também. Sem texto do erro disponível.

## Expected Behavior

Salvar o arquivo (Ctrl+S) com o editor aberto ou depois do OK grava sem erro; o editor trabalha em rascunho e o OK
aplica em um passo de desfazer (RN-16 da 002). O salvar fechado das portas/gavetas (`inspection/save_guard`) não
deve falhar.

## Actual Behavior

No Windows: erro ao salvar (texto desconhecido). **Nova ocorrência (2026-10-07, com o texto do erro):** ao dar OK no
editor de paredes, `apply.apply_plan` → `GeoNodeWall.create` → `bpy.data.libraries.load(...)` falha com
`OSError: load: C:\Users\RYZEN\AppData\Roaming\Blender Foundation\Blender\5.2\extensions\user_default\caffmob_draw\geometry_nodes\GeoNodeWall.blend failed to open blend file`
(`evidence/erro-ok-editor-geonodewall-blend-windows.png`). O "salvar" do relato é o OK do editor. No Linux (2026-10-06, MCP 9876, extensão recém-instalada):
salvar com o editor aberto e salvar depois do OK funcionaram, sem `Traceback`.

## Steps to Reproduce

1. Windows, Blender 5.2.0, plugin instalado como no computador do titular.
2. Abrir o Editor de Paredes (ou usar "Desenhar Paredes").
3. Salvar o arquivo.

## Evidence

- `evidence/reproduction.md` (clone limpo do GitHub reproduz o erro), `evidence/blends-ausentes-no-clone.txt`, `evidence/reproducao-clone-limpo.py`
- Relato: `../../intake/relato-20261006-0900.md` (P3).
- Nova ocorrência com traceback: `../../intake/relato-20261007-2000.md` e `evidence/erro-ok-editor-geonodewall-blend-windows.png`.
- Linux: 2 tentativas sem erro (salvar com o editor aberto; salvar após OK).

## Suspected Area

**Hipótese principal nova (`hypothesized`, a confirmar no fix):** os arquivos `.blend` do pacote `caffmob_draw/` não
estão no git (`.gitignore` tem `*.blend`; o git só rastreia os `.blend` da cópia antiga na raiz:
`git ls-files caffmob_draw | grep geometry_nodes` → 0). O titular clona o repositório do GitHub e gera o zip no Windows
(resposta de 2026-10-07): o pacote sai sem `caffmob_draw/geometry_nodes/GeoNodeWall.blend` (e demais `.blend` de
`caffmob_draw/`), e criar parede falha. Código: `hb_types.py:59` (`GeoNodeObject.create`), `walls2d/apply.py:120`,
`build.py`, `.gitignore`.

Hipóteses anteriores (mantidas para o fix descartar): `inspection/save_guard.py`, `walls2d/window.py`; conflito com a
cópia antiga do plugin carregada junto.

## Acceptance Criteria

- No Windows, salvar com o editor aberto, após OK e após o construtor 3D grava sem erro.
- Um plugin gerado a partir de um clone limpo do GitHub contém todos os `.blend` de que o código precisa
  (`geometry_nodes/`, bibliotecas) e o OK do editor cria as paredes.
- O build avisa (ou falha) se faltar um `.blend` necessário, em vez de gerar um pacote quebrado.
- O console do Windows não mostra `Traceback` ao salvar.

## Traceability

- Specs: `_reversa_forward/002-editor-parede-mover-sobre/requirements.md#RN-16`, `_reversa_sdd/wall_editor/requirements.md`.
- Código: ver Suspected Area.

## Resolution

**Causa raiz (confirmed):** o `.gitignore` ignorava `*.blend`, então os 107 `.blend` do pacote `caffmob_draw/` nunca
foram para o GitHub (só os da cópia antiga na raiz). O titular gera o plugin a partir de um clone no Windows: o zip saía
sem nenhum `.blend`, e criar parede (`GeoNodeWall.create` → `bpy.data.libraries.load`) falhava. Não é específico do
Windows; a hipótese anterior (cópia antiga carregada junto) segue rejeitada.

**Veredito de spec:** `spec-gap` (aprovado por Leonardo Lima em 2026-10-07), adendo
`_reversa_sdd/addenda/bug-BUG-20261006-KFAR-v001.md`.

**resolution_kind:** `fixed`

| CHG | tipo | artefato | propósito |
|---|---|---|---|
| CHG-001 | configuration | `.gitignore` | `!caffmob_draw/**/*.blend` |
| CHG-002 | code | `build.py` | recusa pacote sem os `.blend` usados no código |
| CHG-003 | other | 107 `caffmob_draw/**/*.blend` | rastreados pelo git (`fix/CHG-003-arquivos.txt`) |
| CHG-004 | documentation | `CLAUDE.md` | regra de versionamento |
| CHG-005 | specification | `_reversa_sdd/addenda/bug-BUG-20261006-KFAR-v001.md` | adendo aditivo |

**Testes (vermelho → verde):**
- Antes: `test_blends_do_pacote_estao_no_git` → lista com os 107 `.blend` fora do git;
  `test_build_recusa_pacote_sem_blend` → `0 == 0` (o build gerava o pacote quebrado).
- Depois: `tests/test_packaging.py` 5/5 OK; suíte unitária OK; `ruff` limpo. Ponta a ponta: exportação do índice do git
  (equivalente ao clone) → `build.py` → zip com 107 `.blend` → instalado num Blender limpo → sala 10 x 20 m com 4
  paredes criadas, sem erro.

**Entrega:** o Windows recebe a correção depois do commit/push no `master` + `git pull` e um novo `build.py`.

## Agent Notes

- Não reproduzido no Linux. Para o fix: pedir ao titular o console do Windows (Janela › Alternar Console do Sistema)
  ou o `%TEMP%\blender.crash.txt`, e a lista de add-ons em Preferências › Add-ons do Windows.
- Hipótese principal (`proposed`): cópia antiga/add-on legado `blendertomob` carregado junto da extensão nova
  (ver relação).
- Prioridade P0 assumida (titular informou só "critical").
- 2026-10-07: titular pediu "faça que este erro não aconteça mais"; instalação no Windows = clone do GitHub + build.py.
