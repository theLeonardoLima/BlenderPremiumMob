# Legacy impact: 009-mira-calculo-skp-biblioteca

> Data: 2026-10-09. Rodada única do `/reversa-coding` (43 ações: T001–T046, sem T004, T009 e T017).
> Base: `_reversa_sdd/architecture.md` (componentes `wall_editor`, `geometry / mesh_gen`, `cutting / nesting`, dívida
> D-02) e `_reversa_sdd/domain.md` (R-01 a R-10).

## Arquivos afetados

| Arquivo afetado | Componente | Tipo | Severidade | Justificativa |
|---|---|---|---|---|
| `caffmob_draw/walls2d/ops_editor.py` | Editor de paredes 2D (`_reversa_sdd/wall_editor`) | regra-alterada | HIGH | Mira com alinhamento X/Y; cadeia única de travas (`resolve_point`); Enter segue a direção travada, que só muda por clique ou setas; conta na medida |
| `caffmob_draw/walls2d/props.py` | Editor de paredes: sessão | delta-de-dados | LOW | Direção atual, travas da mira, prévia da conta e índice do alinhamento (memória) |
| `caffmob_draw/walls2d/inference.py`, `direction.py` | Editor de paredes: núcleos | componente-novo | LOW | Puros, testados; o índice ordenado resolve a dívida D-02 para o alinhamento |
| `caffmob_draw/data/expr.py` | Medidas digitadas | componente-novo | MEDIUM | Analisador de conta sem `eval` |
| `caffmob_draw/data/units.py` | Medidas digitadas (`parse_length`) | regra-alterada | MEDIUM | Delega a `expr` quando há conta: `3/4` deixa de ser recusado (PL-03 da 001) e vira 0,75 mm |
| `caffmob_draw/object_library/` (`catalog`, `store`, `props`, `item_io`, `retexture`, `ops`, `panels`, `previews`) | Biblioteca de objetos | componente-novo | MEDIUM | Itens com manifesto, inserir com modal, acrescentar, retexturizar |
| `caffmob_draw/object_library/items/` | Biblioteca de objetos: itens embutidos | componente-novo | LOW | 6 itens modelados pelo projeto (1,5 MB), sem modelos de terceiros |
| `caffmob_draw/library_common.py`, `caffmob_draw/customize/library_io.py` | Biblioteca de módulos (003) | regra-alterada | LOW | Miniatura e caixa movidas para um módulo comum, sem mudança de comportamento |
| `caffmob_draw/aggregates/skp.py`, `skp_core.py`, `skp_build.py` | Importar modelo: SketchUp | componente-novo | MEDIUM | OpenSKP; montagem no Blender com grupos, materiais nomeados e texturas empacotadas |
| `caffmob_draw/aggregates/ops_import.py` | Importar modelo (003/007) | regra-alterada | MEDIUM | `.skp` passa a ser aceito; falha não cria nada |
| `caffmob_draw/wheels/`, `caffmob_draw/blender_manifest.toml` | Empacotamento da extensão | delta-de-contrato-externo | MEDIUM | 12 wheels (openskp, defusedxml, mapbox_earcut, shapely) declaradas no manifesto; instalação verificada num Blender limpo |
| `caffmob_draw/__init__.py` | Registro da extensão | regra-alterada | LOW | Registra `object_library` |
| `caffmob_draw/ui/sidebar_insert.py`, `sidebar_selected.py`, `sidebar_props.py` | Barra lateral (005) | regra-alterada | LOW | Grupos "Objetos" (Inserir) e "Retexturizar" (Selecionado) |
| `build.py` | Empacotamento | regra-alterada | LOW | Exige as wheels e a biblioteca embutida; recusa um item embutido do 3D Warehouse |
| `.gitignore` | Repositório | regra-alterada | MEDIUM | Exceção `!caffmob_draw/wheels/` (a regra `wheels/` deixaria um clone sem o leitor de SketchUp) |
| `caffmob_draw/data/translations/*.json` | Tradução | regra-nova | LOW | 77 textos pt-BR/en-US (`object_library.json` novo) |
| `tools/fetch_wheels.py`, `build_object_library.py`, `make_skp_fixture.py` | Ferramentas | componente-novo | LOW | Reprodutíveis: wheels por SHA-256, itens embutidos, `.skp` de teste |
| `tests/test_measure_expr.py`, `test_wall_inference.py`, `test_wall_direction.py`, `test_object_library.py`, `test_skp_core.py`, `blender_009_*_smoke.py`, `fixtures/porta_teste.skp`, `_bootstrap.py`, `_blender_env.py` | Testes | regra-nova | LOW | 32 testes unitários novos, 3 fumaças; o ambiente de teste instala as wheels e pode compartilhar a pasta do usuário |
| `tests/blender_002_smoke.py`, `blender_002_ui_events.py`, `blender_003_aggregates_smoke.py`, `test_units.py` | Testes antigos | regra-alterada | LOW | Ajustados à RN-06 (setas), à RN-04 (`3/4`) e ao `.skp` suportado |
| `docs/usuario/editor-paredes-e-mover-sobre.md`, `docs/usuario/biblioteca-de-objetos.md` | Documentação | regra-alterada | LOW | Mira, conta e direção; guia novo da biblioteca e do SketchUp |

## Diff conceitual por componente

**Editor de paredes.** Antes, o lápis calculava a direção do Enter a partir do cursor. Depois de um Enter, o último
ponto ia para a frente do cursor e o próximo Enter podia inverter a direção. Agora a direção é estado da sessão:
- nasce do primeiro movimento, com a trava ortogonal;
- muda só pelo clique (direção do trecho criado) ou pelas setas do teclado.

As travas do ponto (ímã do início, vértice, alinhamento X/Y, ortogonal, grade) passaram para uma função única. O ponto
desenhado e o clicado são os mesmos, e a trava ortogonal e o alinhamento combinam: uma parede reta termina pareada
com o canto do outro lado. Shift desliga só o alinhamento. A digitação aceita conta, com a prévia "= 16 mm".

**Medidas.** `parse_length` continua igual para números simples e passa a delegar contas a `data/expr.py`. A única
mudança visível em textos antigos: `3/4` era recusado como fração de polegada e agora vale 0,75 mm.

**Biblioteca de objetos.** O pacote novo reaproveita a mecânica da biblioteca de módulos da 003 (`.blend` +
manifesto + miniatura). A raiz do item é um grupo de peças da 007, e as conversões (folha, esquadria, agregado, peça
de produção) ficam gravadas nos próprios objetos, por isso voltam ao inserir. Inserir usa um modal próprio, para o
Esc remover o item. Retexturizar usa `common.set_cutpart_material` da 003 (chapas nas duas faces) ou um material de
imagem com projeção em caixa.

**SketchUp.** O OpenSKP lê o `.skp` em Python puro. O núcleo converte Y-up em Z-up, descarta o verso duplicado,
dá aos materiais os nomes do SketchUp e grava as texturas; a montagem cria malhas e grupos de peças. As dependências
entram como wheels da extensão, e o Blender instala só as da plataforma.

## Preservadas

Regras 🟢 de `_reversa_sdd/domain.md` que continuam intactas:
- R-01 (piso só com paredes), R-02 (piso pelo perímetro interno), R-03 (o sentido define o lado da espessura): a
  direção travada só escolhe o rumo do trecho, e o lado da espessura continua vindo do sentido. A sala desenhada
  fecha com a espessura para fora (fumaças da 002).
- R-04 a R-08 (aberturas de ambiente): fora do escopo.
- R-09, R-10 (nesting): a mesa embutida entra no plano de corte pelo caminho de peças de produção da 003, e o
  algoritmo não mudou.

## Modificadas

Nenhuma regra 🟢 de `_reversa_sdd/domain.md` foi alterada ou removida.

Mudaram regras de features anteriores que não estão no `domain.md`: o Enter do lápis da 002 (agora segue a direção
travada), a decisão PL-03 da 001 (`3/4` vira conta) e o formato recusado da 003 (`.skp` agora é aceito). Elas ficam em
"Observações" no `regression-watch.md`.
