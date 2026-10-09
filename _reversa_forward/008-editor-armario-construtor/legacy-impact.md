# Legacy impact: 008-editor-armario-construtor

> Data: 2026-10-08. Rodada única do `/reversa-coding` (T001–T063, sem T058).
> Base: `_reversa_sdd/architecture.md` (componentes `geometry / mesh_gen` e `cutting / nesting`, e o fluxo de
> exportação do plano de corte) e `_reversa_sdd/domain.md` (R-01 a R-10).

## Arquivos afetados

| Arquivo afetado | Componente | Tipo | Severidade | Justificativa |
|---|---|---|---|---|
| `caffmob_draw/cabinet_editor/catalog.py`, `extras.py`, `bays.py`, `slides.py`, `appliances.py`, `position.py` | Editor de armário: núcleos puros | componente-novo | LOW | Catálogo do Construtor e regras geométricas, testados fora do Blender |
| `caffmob_draw/cabinet_editor/divisions.py` | Editor de armário: divisões (006) | regra-alterada | MEDIUM | Tipos `MOVABLE`/`SPACER`, `follow`, `add_many`, `remove_in_space`; o distanciador ocupa a faixa sem criar subvãos |
| `caffmob_draw/cabinet_editor/structure.py`, `geometry/mesh_gen.py`, `data/properties.py` | Módulo `btm`: malha da caixa | regra-alterada | MEDIUM | `back_setback` desloca o fundo para dentro e recorta o vão. Com 0, a malha fica igual à de antes |
| `caffmob_draw/cabinet_editor/data_props.py`, `props.py`, `state.py` | Editor de armário: dados | delta-de-dados | MEDIUM | `Object.btm_extra`, extras, fundo, campos de divisão (`bay`, `kind`, `follow`), opções das 7 abas; o rascunho guarda extras, deslizantes, internos e fundos |
| `caffmob_draw/cabinet_editor/scene_parts.py`, `scene_extras.py`, `scene_interiors.py`, `scene_slides.py` | Editor de armário: peças na cena | componente-novo | MEDIUM | Chapas `CabinetPart` filhas da raiz, ferragens e eletros de referência; deslizantes como grupo FRAME/LEAF da 007 |
| `caffmob_draw/cabinet_editor/bridge.py`, `ops_editor.py`, `ops_actions.py`, `window.py` | Editor de armário: ponte, modal e vista | regra-alterada | HIGH | Inserir por aba, Aplicar (`ed.undo_push` + nova referência do Cancelar), setas com passo, seleção de vão e de peça, barra "Selecionado" |
| `caffmob_draw/cabinet_editor/panels*.py`, `previews.py`, `thumbnails/`, `__init__.py` | Editor de armário: interface | regra-alterada | MEDIUM | 7 abas com ícones; a aba Acabamento (006) saiu, e o conteúdo dela foi para Estrutura (Materiais) e Divisões (Interior da biblioteca) |
| `caffmob_draw/customize/adapters/*.py`, `customize/props.py` | Personalização (003): adaptadores | regra-alterada | MEDIUM | `set_back_recess` por `delta_location`; `slide_kind` no vão |
| `caffmob_draw/customize/reapply.py` | Personalização: reaplicar | regra-alterada | MEDIUM | `after_rebuild` também reafirma o recuo e reposiciona extras, internos e deslizantes |
| `caffmob_draw/cutting/part_sources.py` | `cutting`: fontes de peças | regra-alterada | HIGH | Uid único entre peças sintéticas e reais do `btm` (corrige colisão `POR/0`, `PRAT/0`); ferragens fora; `iter_modules(ensure_uid=False)`; chave da peça |
| `caffmob_draw/cutting/nesting.py`, `part_extractor.py` | `cutting / nesting`: peça de produção | delta-de-dados | LOW | `NestingPart.drilling`; o algoritmo de nesting não mudou |
| `caffmob_draw/cutting/drilling.py`, `hardware.py` | `cutting`: furação e ferragens | componente-novo | MEDIUM | Linhas de pino de prateleira das móveis; lista de ferragens por código e módulo |
| `caffmob_draw/cutting/json_exporter.py`, `operators/ops_cutting.py` | Exportação do plano de corte (JSON) | delta-de-contrato-externo | HIGH | 2.1.0 → **2.2.0**: `hardware[]`, `parts[].drilling` preenchido; o leitor aceita 2.0 a 2.2 (`interfaces/cut-plan-json.md`) |
| `caffmob_draw/ui/sidebar_project.py` | Barra lateral (005): Produção | regra-nova | LOW | Caixa "Ferragens", recolhida, no Plano de corte |
| `caffmob_draw/data/translations/cabinet_editor.json`, `cutting.json` | Tradução | regra-nova | LOW | 203 textos pt-BR/en-US (abas, catálogo, mensagens, ferragens) |
| `tools/render_cabinet_thumbnails.py` | Ferramentas | componente-novo | LOW | Gera as 47 miniaturas do catálogo (Workbench) |
| `tests/test_cabinet_*.py`, `tests/blender_008_construtor_smoke.py`, `tests/test_production_contracts.py` | Testes | regra-nova | LOW | Núcleos, contrato 2.2.0, fumaça nas 4 bibliotecas |
| `tests/blender_006_cabinet_editor_tabs_smoke.py`, `blender_smoke.py`, `blender_increment1_smoke.py`, `blender_003_aggregates_smoke.py` | Testes antigos | regra-alterada | LOW | Abas novas no lugar de FINISH; versão do JSON "2.2.0" |
| `docs/usuario/editor-de-armario.md` | Documentação | regra-alterada | LOW | Guia reescrito para as 7 abas, Aplicar e produção |

## Diff conceitual por componente

**Editor de armário.** O editor da 006 (Estrutura, Divisão, Acabamento) vira o Construtor de Armários do Promob, com
sete abas e o ciclo "vão → aba → item → Inserir → Aplicar/OK":
- toda aba de inserção diz em qual vão vai inserir, e sem vão o Inserir fica apagado com o motivo;
- Gavetas e Portas inserem no vão da biblioteca que contém o vão escolhido;
- Aplicar grava um passo de desfazer na cena sem fechar e vira a referência do Cancelar. OK continua sendo "aplicar e
  fechar".

As peças novas (extras, internos, folhas de correr) são filhas diretas da raiz, marcadas com `btm_extra`, como as
divisões da 006. Por isso a biblioteca não as apaga quando reconstrói o módulo.

**Divisões.** Além da fixa, há a **móvel**, com a mesma geometria e a furação nas peças vizinhas, e o
**distanciador**. Ele ocupa uma faixa do lado sem criar dois subvãos: o subvão continua com o mesmo caminho e fica com
o lado maior. "Sem Divisória" remove a divisória que criou o vão e as de dentro dela. Número de vãos gera divisórias
`bay` que dividem o vão interno em partes iguais.

**Fundo recuado.** No `btm`, o `layout` da 006 desloca o fundo e recorta o vão. Nas bibliotecas de peças, a peça do
fundo anda pelo `delta_location`, que drivers e recálculos não sobrescrevem, e o `after_rebuild` reafirma o recuo.

**Produção.** O plano de corte passa a ter extras, distanciadores, painéis de eletro e folhas de correr; ferragens e
eletros de referência ficam de fora. O JSON 2.2.0 traz:
- a lista de ferragens, somada por código e módulo;
- a furação das móveis, no referencial de cada peça vizinha e recortada ao comprimento dela (`MACHINING_CLIPPED`).

A fumaça achou um defeito no uid: no `btm`, peças sintéticas e reais repetiam o índice por componente. Agora as duas
listas são numeradas juntas, e os uids que já existiam continuam iguais.

## Preservadas

Regras 🟢 de `_reversa_sdd/domain.md` que continuam intactas:
- R-01, R-02, R-03 (paredes e piso): a mudança em `geometry/mesh_gen.py` só acrescenta `back_setback` à caixa do
  módulo. O fecho convexo do piso (`_convex_hull_2d`) não foi tocado.
- R-04 a R-08 (aberturas de ambiente): fora do escopo.
- R-09, R-10 (nesting por área e corte guilhotinado): `NestingPart` ganhou o campo `drilling`, que o algoritmo não lê.
  A ordem, as faixas e o kerf não mudaram (`tests/test_production_contracts.py` e as fumaças do plano de corte
  passam).

## Modificadas

Nenhuma regra 🟢 de `_reversa_sdd/domain.md` foi alterada ou removida.

As mudanças de comportamento valem para regras das features 003, 004 e 006 (contrato JSON 2.1.0, aba Acabamento,
Confirmar/Cancelar) e para o uid das peças do `btm`. Nenhuma delas está no `domain.md`, e todas ficam em
"Observações" no `regression-watch.md`.
