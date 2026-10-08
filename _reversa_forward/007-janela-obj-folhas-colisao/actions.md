# Actions: Janela importada (OBJ) com folhas de correr, agregados por grupo e colisão coerente

> Identificador: `007-janela-obj-folhas-colisao`
> Data: `2026-10-08`
> Roadmap: `_reversa_forward/007-janela-obj-folhas-colisao/roadmap.md` (D-01 a D-14)
> Data delta: `_reversa_forward/007-janela-obj-folhas-colisao/data-delta.md`
> Interfaces: nenhuma
> Incrementos:
> - I1: núcleos puros (T009–T012)
> - I2: importação (T014)
> - I3: grupo e Montar esquadria (T013, T015, T016, T020, T021)
> - I4: colisão (T017–T019, T024)
> - I5: parede (T022, T023, T027)
>
> Caminhos relativos à raiz do repositório. Arquivo de teste real: `_reversa_forward/007-janela-obj-folhas-colisao/inputs/janela_preta_1400mm.obj`.

## Resumo

| Métrica | Valor |
|---------|-------|
| Total de ações | 30 |
| Paralelizáveis (`[//]`) | 23 |
| Maior cadeia de dependência | 9 (T001 → T013 → T015 → T018 → T019 → T021 → T025 → T029 → T030) |
| Ordem de entrega | I1 → I2 → I3 → I4 → I5; a fumaça (T029) usa o OBJ real |

## Fase 1, Preparação

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T001 | `BTM_PG_GroupMember` (`obj`, `orig_parent`, `orig_matrix`) e `BTM_PG_Group` (`is_group`, `kind` FRAME/LEAF/PLAIN, `members`) em `Object.btm_group`, com `register`/`unregister` (data-delta §1.1) | - | `[//]` | `caffmob_draw/aggregates/group_props.py` | 🟢 | `[X]` |
| T002 | `BTM_PG_WindowInstall` (`frame`, `frame_matrix`) em `Object.btm_window`, com `register`/`unregister` (data-delta §1.2) | - | `[//]` | `caffmob_draw/aggregates/window_props.py` | 🟢 | `[X]` |
| T003 | `BTM_PG_Aggregate` ganha `contact_kind` (NONE/OPEN/CLOSE), `free_travel` e `rest_overlap`. O `update` de `travel` limita ao `free_travel` quando ele for > 0 (data-delta §1.3, §3) | - | `[//]` | `caffmob_draw/aggregates/props.py` | 🟢 | `[X]` |
| T004 | `cut_wall(wall, cutter)` vira função de módulo (o método da mixin passa a chamá-la), para uso fora do modal de janelas (D-12) | - | `[//]` | `caffmob_draw/operators/doors_windows.py` | 🟢 | `[X]` |

## Fase 2, Testes

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T005 | Testes da unidade: escala por unidade (mm 0,001; cm 0,01; m 1; pol 0,0254) e sugestão AUTO (maior medida > 50 → mm; 0,8 → m) | - | `[//]` | `tests/test_import_units.py` | 🟢 | `[X]` |
| T006 | Testes da sugestão de grupos: os 46 nomes do OBJ geram Folha_Esquerda 15, Folha_Direita 15 e Esquadria 16; nomes sem `Folha` viram um grupo só; sufixos `.001` não quebram o prefixo; lista vazia | - | `[//]` | `tests/test_grouping.py` | 🟡 | `[X]` |
| T007 | Testes dos limites do correr com as caixas reais do arquivo (mm): sentido padrão para o próprio lado (esquerda → NEG_X); aviso de pouco curso (2 mm < 10% de 692 mm); sobreposição dos montantes em repouso = 32 mm; `close_stop` com a outra folha em repouso (= posição do arquivo) e com a outra folha deslocada | - | `[//]` | `tests/test_slide_limits.py` | 🟡 | `[X]` |
| T008 | Testes da varredura nos dois sentidos: fechar livre mantém o comportamento da 003; fechar com `hit` para no contato; fechar com limite mínimo para no limite | - | `[//]` | `tests/test_leaf_sweep.py` | 🟢 | `[X]` |

## Fase 3, Núcleo

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T009 | Núcleo puro da unidade: `SCALE`, `suggest(maior_medida)`, `scale_for(unidade, maior_medida)` (D-01) | T005 | `[//]` | `caffmob_draw/aggregates/import_units.py` | 🟢 | `[X]` |
| T010 | Núcleo puro dos grupos: prefixo de dois tokens para `Folha`/`Leaf`/`Sash`, o resto vira esquadria; devolve `[(nome, papel, [nomes])]` em ordem estável (D-04) | T006 | `[//]` | `caffmob_draw/aggregates/grouping.py` | 🟡 | `[X]` |
| T011 | Núcleo puro do correr: `default_direction(folha, esquadria)`, `low_travel(livre, largura)`, `rest_overlap(a, b)`, `close_stop(posição, sentido, outra folha, sobreposição)` em 1D sobre o eixo do trilho (D-08, D-10) | T007 | `[//]` | `caffmob_draw/aggregates/slide_limits.py` | 🟡 | `[X]` |
| T012 | `sweep.sweep` aceita fechar com teste de contato e um limite mínimo opcional (`floor`), mantendo "fechar livre" quando chamado como na 003 (D-10) | T008 | `[//]` | `caffmob_draw/aggregates/sweep.py` | 🟢 | `[X]` |
| T013 | Grupo na cena: `create_group(objs, kind, name)` (Empty no centro da base da caixa, peças filhas com a matriz do mundo preservada e origem guardada), `ungroup(group)`, `members(group)` e `group_box(group, space)` (união das peças avaliadas) (D-03) | T001 | `[//]` | `caffmob_draw/aggregates/group.py` | 🟢 | `[X]` |
| T014 | Importação com `unit` e `up_axis`: OBJ via `wm.obj_import(global_scale, up_axis, forward_axis)`; FBX via `import_scene.fbx(global_scale, axis_up)`; AUTO mede e reescala; o relatório diz a unidade (D-01, D-02) | T009 | `[//]` | `caffmob_draw/aggregates/ops_import.py` | 🟢 | `[X]` |
| T015 | Folha de grupo: `leaf_box` e `make_leaf` usam `group_box` quando o objeto é grupo; `make_leaf` grava `rest_overlap` com a outra folha do mesmo pai FRAME (D-05, D-10) | T003, T013 | `[//]` | `caffmob_draw/aggregates/leaf.py` | 🟢 | `[X]` |
| T016 | `can_convert` aceita um Empty de grupo como folha e um grupo FRAME como pai; recusa Empty que não é grupo (D-05) | T013 | `[//]` | `caffmob_draw/aggregates/convert.py` | 🟢 | `[X]` |
| T017 | Colisão: os cantos do `Tester` saem de `group_box` (espaço da folha); `_excluded` deixa de tirar as peças da esquadria quando o pai é grupo FRAME e tira as folhas irmãs e as peças de cada folha (D-05, D-07) | T013 | `[//]` | `caffmob_draw/aggregates/collision.py` | 🟢 | `[X]` |
| T018 | `update_open` com varredura nos dois sentidos para folha com pai FRAME: abrir para na esquadria; fechar para no primeiro de (a) fração 0, (b) `close_stop` com a posição atual da outra folha e (c) contato. Grava `contact_name` e `contact_kind` (D-10, D-11) | T011, T012, T015, T017 | - | `caffmob_draw/aggregates/leaf.py` | 🟡 | `[X]` |
| T019 | Correr na esquadria: sentido padrão por `default_direction`; `free_travel` medido pela varredura até a largura da esquadria; `travel` = livre; flag de pouco curso para o painel (D-08, D-09) | T018 | - | `caffmob_draw/aggregates/leaf.py` | 🟡 | `[X]` |
| T020 | Operadores "Criar grupo" (seleção → grupo PLAIN, com nome) e "Desfazer grupo" (`UNDO`); sem malha selecionada ficam indisponíveis com "Selecione as peças do grupo" (RN-04) | T013 | `[//]` | `caffmob_draw/aggregates/ops_group.py` | 🟢 | `[X]` |
| T021 | Operador "Montar esquadria": o diálogo lista os grupos sugeridos (`grouping`) com a quantidade e o papel editável (Esquadria, Folha de correr, Folha de giro, Ignorar). Ao confirmar, cria a esquadria FRAME, as folhas como filhas e as converte (correr com D-08/D-09) num passo de desfazer (D-06) | T010, T019, T020 | - | `caffmob_draw/aggregates/ops_group.py` | 🟡 | `[X]` |
| T022 | Instalação: `install(frame, wall, x, sill)` cria `GeoNodeCage` `IS_WINDOW_BP` com as medidas da esquadria e a espessura da parede, filho da parede, corta com `cut_wall` e prende a esquadria centrada na espessura. `uninstall(cage)` solta a esquadria na matriz do mundo, remove o boolean e apaga a jaula. Parede não HB → mensagem de conversão (D-12, D-13, D-14) | T002, T004, T013 | `[//]` | `caffmob_draw/aggregates/install.py` | 🟢 | `[X]` |
| T023 | Operadores "Instalar na parede" (esquadria + parede selecionadas; posição pelo centro da esquadria projetado na parede; peitoril 1,0 m) e "Desinstalar" (`UNDO`) | T022 | `[//]` | `caffmob_draw/aggregates/ops_install.py` | 🟢 | `[X]` |
| T024 | Overlay: destaque da caixa da peça de contato (abrir ou fechar) além da folha; texto "bateu em"/"encostou em" na vista (D-11) | T003 | `[//]` | `caffmob_draw/aggregates/overlay.py` | 🟢 | `[X]` |
| T025 | Painel: Criar/Desfazer grupo e Montar esquadria junto de Converter; na folha, o aviso de pouco curso e o texto do contato por tipo; no grupo FRAME, Instalar/Desinstalar | T019, T021, T023 | - | `caffmob_draw/aggregates/panels.py` | 🟡 | `[X]` |

## Fase 4, Integração

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T026 | Registro no pacote `aggregates`: `group_props`, `window_props`, `ops_group` e `ops_install`, na ordem certa; o `unregister` desfaz tudo | T001, T002, T020, T021, T023 | - | `caffmob_draw/aggregates/__init__.py` | 🟢 | `[X]` |
| T027 | Editor de paredes: depois de atualizar `Dim Y` de uma janela (`walls2d/apply.py:152`), recentrar a esquadria instalada (`btm_window.frame`) na espessura nova | T022 | `[//]` | `caffmob_draw/walls2d/apply.py` | 🟡 | `[X]` |

## Fase 5, Polimento

| ID | Descrição | Dependências | Paralelismo | Arquivo alvo | Confidência | Status |
|----|-----------|--------------|-------------|--------------|-------------|--------|
| T028 | Traduções pt-BR/en-US dos textos novos (unidade, eixo, grupos, Montar esquadria, avisos de contato e de curso, instalar) | T014, T021, T023, T025 | `[//]` | `caffmob_draw/data/translations/aggregates.json` | 🟢 | `[X]` |
| T029 | Fumaça com o OBJ real cobrindo, cada item com um passo de desfazer conferido: importar AUTO em 1400 × 850 × 80 mm e em pé, com 46 peças e 4 materiais; Montar esquadria 15/15/16; folha esquerda invertida abrindo até o marco direito; voltar à posição do arquivo; encostar no montante da direita aberta; aviso de pouco curso no sentido padrão; instalar numa parede HB (vão cortado, limite no segmento), mudar a espessura no editor e desinstalar | T025, T026, T027, T014 | - | `tests/blender_007_window_smoke.py` | 🟡 | `[X]` |
| T030 | Guia do usuário: importar com unidade e eixo, grupos, Montar esquadria, abrir/fechar com batentes e instalar na parede | T029 | - | `docs/usuario/agregados-e-folhas.md` | 🟢 | `[X]` |

## Notas de execução

- T015, T018 e T019 compartilham `leaf.py` e por isso são sequenciais; T015 aparece como `[//]` só em relação às
  ações de outros arquivos.
- T020 e T021 compartilham `ops_group.py`, então T021 vem depois de T020.
- T029 deve rodar também as fumaças da 003 (`blender_003_aggregates_smoke.py`), porque folha, colisão e varredura são
  compartilhadas.
- Premissa do roadmap §4: o sentido padrão é "para o próprio lado", com aviso de pouco curso. Se o titular mudar isso,
  só T011/T019 mudam.
- 2026-10-08 (rodada única, T001–T030): desvios e decisões tomadas no código, sem mudar o escopo:
  - T011/T018: o batente (b) "montante da outra folha" é `close_stop = max(0, sA · dB)`: a folha A, que abre no
    sentido `sA`, não fecha além do deslocamento atual `dB` da outra folha projetado no sentido dela. Mantém a relação
    dos montantes do arquivo e, com a outra folha no lugar, coincide com a pose do arquivo.
    - Neste OBJ ele aparece quando a direita, invertida para o centro, anda para dentro do lado da esquerda: a
      esquerda (padrão, para o próprio lado) não fecha além dela.
    - Com as duas para o centro, elas se cruzam em trilhos diferentes e não se travam.
    - O cenário Gherkin "Folha encosta na outra folha ao fechar" do requirements foi testado nesse arranjo.
  - T019: ao chegar ao fim do curso livre, a folha cita a peça da esquadria medida (`btm_free_contact`), porque o
    curso já para no contato e a varredura não "bate" de novo.
  - T027: sem mudança em `walls2d/apply.py`. A esquadria é centrada por drivers na jaula (x = Dim X/2,
    y = Dim Y/2), e o editor de paredes já muda o `Dim Y` das janelas.
  - T013/T029: `ungroup` atualiza a cena antes de ler as matrizes. A fumaça pegou as peças 2,5 mm fora depois de
    desconverter a folha.
  - T029: a fumaça roda em segundo plano. O desfazer de verdade (Ctrl+Z) pede janela; a fumaça confere que os seis
    operadores novos têm `UNDO`, e o passo a passo fica no onboarding.
  - T021: as folhas convertidas ficam filhas do pivô (003), e não da esquadria; "Desfazer grupo" procura as folhas em
    `children_recursive`.

## Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-10-08 | Versão inicial gerada por `/reversa-to-do` | reversa |
| 2026-10-08 | `/reversa-coding`: T001–T030 concluídas; notas de execução | reversa |
