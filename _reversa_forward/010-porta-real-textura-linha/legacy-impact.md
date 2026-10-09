# Legacy impact: 010-porta-real-textura-linha

> Data: 2026-10-09. Rodada única do `/reversa-coding` (T001–T034).
> Base: `_reversa_sdd/architecture.md` (aberturas e colocação, `geometry`, barra lateral), `_reversa_sdd/domain.md`
> (R-01 a R-10), `_reversa_sdd/hb_placement/requirements.md` (RN-10, RN-20, RN-21).

## Arquivos afetados

| Arquivo afetado | Componente | Tipo | Severidade | Justificativa |
|---|---|---|---|---|
| `caffmob_draw/operators/doors_windows.py` | Portas e janelas de ambiente (colocação, prompts, inverter giro e mão) | regra-alterada | HIGH | Montagem da porta/janela real ao confirmar e nos prompts; a medida digitada da porta é a da folha (a caixa ganha o marco) |
| `caffmob_draw/hb_props.py` | Propriedades do projeto | regra-alterada | MEDIUM | Padrões 80/160 × 210 (eram 36"/72" × 84"); "Mostrar caixas" mostra a caixa em arame quando há porta real |
| `caffmob_draw/openings/` (`door_core`, `window_core`, `materials`, `build`, `sync`, `props`, `ops`, `assets/`) | Aberturas reais | componente-novo | MEDIUM | Geradores paramétricos (da porta realista do projeto), materiais compartilhados, montagem em poucas malhas, `sync` na caixa, "Atualizar portas e janelas" |
| `caffmob_draw/aggregates/collision.py` | Folha de porta: colisão (003/007) | regra-alterada | MEDIUM | O marco de uma porta/janela real não é obstáculo para as folhas dela; paredes, móveis e o resto continuam |
| `caffmob_draw/walls2d/apply.py` | Editor de paredes | regra-alterada | LOW | Depois de aplicar, refaz as aberturas cujas medidas mudaram (assinatura) |
| `caffmob_draw/aggregates/skp_core.py`, `skp_build.py`, `ops_import.py` | Leitor de SketchUp (009) | regra-alterada | MEDIUM | Árvore com instâncias aninhadas e repetidas, figuras de escala puladas, material reaproveitado e sem `Layer_` |
| `caffmob_draw/ui/view_mode.py`, `view_mode_core.py`, `sidebar_build.py` | Barra lateral (005) e vista | componente-novo | LOW | Modo Sólido · Textura e interruptor Linhas, salvos na cena, com `load_post`; aviso de caixas antigas |
| `caffmob_draw/__init__.py` | Registro da extensão | regra-alterada | LOW | Registra `openings` (e o `ui/view_mode`) |
| `build.py` | Empacotamento | regra-alterada | LOW | Exige as texturas da porta em `openings/assets/` |
| `.gitignore` | Repositório | regra-alterada | LOW | Da porta realista do Codex, só o gerador e o LEIA-ME entram |
| `caffmob_draw/data/translations/{openings,sidebar,aggregates}.json` | Tradução | regra-nova | LOW | 17 textos pt-BR/en-US |
| `tools/build_openings_assets.py`, `render_openings_preview.py`, `make_skp_fixture.py` | Ferramentas | componente-novo | LOW | Texturas em JPG, prévias no estilo `product-polish`, `porta_aninhada.skp` |
| `tests/test_skp_tree.py`, `test_door_core.py`, `test_window_core.py`, `test_view_mode.py`, `blender_010_*`, `_openings_env.py`, `fixtures/porta_aninhada.skp` | Testes | regra-nova | LOW | 24 unitários e 3 fumaças novas |
| `docs/usuario/editor-paredes-e-mover-sobre.md`, `biblioteca-de-objetos.md` | Documentação | regra-alterada | LOW | Portas e janelas reais, modo de vista, hierarquia do SketchUp |

## Diff conceitual por componente

**Portas e janelas de ambiente.** A caixa (`GeoNodeCage`) continua sendo o objeto que se prende à parede, desliza,
troca de segmento e corta o furo (R-04 a R-08), e a colocação segue a mesma. O que muda:
- dentro da caixa entra a porta ou a janela real, montada por `openings/sync.py`: um grupo FRAME alinhado aos eixos
  da caixa, com folhas da 003/007;
- a caixa passa a arame, e o texto some da vista 3D; o símbolo 2D de giro continua e define o lado e o sentido;
- na porta, a medida digitada passa a ser a da folha, e o furo é calculado para caber o marco.

**Colisão da folha.** Com a porta real, a folha fechada encosta no próprio marco (dobradiças, lingueta). O marco da
montagem deixou de ser obstáculo para as folhas dela. Na janela, o batente virou curso geométrico.

**SketchUp.** O plano de montagem da 009 era plano por caminho; agora é a árvore da cena do OpenSKP, e o `plan()` da
009 continua como percurso dessa árvore.

**Vista.** Um controle novo aplica os ajustes de `View3DShading` e `View3DOverlay` nas vistas 3D. As configurações
recomendadas do legado (`ops.py`) não mudaram.

## Preservadas

Regras 🟢 de `_reversa_sdd/domain.md` que continuam intactas:
- **R-04 a R-08 (aberturas):**
  - a porta segue presa ao segmento (herda rotação e espessura, agora também na montagem);
  - o furo continua sendo a caixa;
  - o movimento é preso ao plano e ao comprimento da parede, e a troca de segmento e o peitoril fixo da porta não
    mudaram.

  As fumaças da 002, 004 e 005 passaram.
- **R-01 a R-03 (paredes e piso):** não foram tocadas. O `walls2d/apply.py` só ganhou o refazer das aberturas no fim.
- **R-09, R-10 (nesting):** as peças da porta ficam fora do corte por padrão.
- **`hb_placement` RN-10, RN-20, RN-21:** o vão livre e os recuos usam a caixa, que continua com `IS_ENTRY_DOOR_BP` e
  `IS_WINDOW_BP`.

## Modificadas

Nenhuma regra 🟢 de `_reversa_sdd/domain.md` foi alterada ou removida.

Mudaram comportamentos que não estão no `domain.md` e vão para "Observações" no `regression-watch.md`:
- as medidas padrão;
- a medida digitada da porta (folha);
- o marco como não-obstáculo da própria folha;
- o plano em árvore do SketchUp.
