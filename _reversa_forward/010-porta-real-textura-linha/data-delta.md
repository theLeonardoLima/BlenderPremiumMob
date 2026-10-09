# Data delta: 010-porta-real-textura-linha

> Data: 2026-10-09.

## 1. Cena: modo de vista (RN-06, D-05)

| Campo | Tipo | Padrão | Uso |
|---|---|---|---|
| `Scene.btm_view_mode` | Enum `SOLID`/`TEXTURE` | `SOLID` | Modo das vistas 3D |
| `Scene.btm_view_lines` | Bool | False | Arestas em todos os objetos |
| `Scene.btm_view_prev_color` | String | "" | `color_type` anterior, devolvido ao voltar a Sólido |

Ficam salvos no arquivo. O `load_post` reaplica nas vistas.

## 2. Caixa de porta e janela: `Object.btm_opening` (D-10, D-11, D-16)

| Campo | Tipo | Padrão | Uso |
|---|---|---|---|
| `kind` | Enum `NONE`/`DOOR`/`DOUBLE_DOOR`/`OPEN_DOOR`/`WINDOW` | `NONE` | O que foi montado na caixa (`NONE` = caixa antiga, sem a porta real) |
| `signature` | String | "" | Dim X, Y e Z, lado e sentido da última montagem; igual = não refaz |
| `model_version` | Int | 1 | Versão do gerador (para atualizar portas antigas) |
| `assembly` | Pointer Object | None | Grupo FRAME montado |

Os grupos FRAME e LEAF usam os campos `btm_group` e `btm_aggregate` (003/007), sem mudança.

## 3. Padrões de `Scene.home_builder` (D-13)

`door_single_width` 0,9144 → 0,80; `door_double_width` 1,8288 → 1,60; `door_height` 2,1336 → 2,10. Só vale para
cenas novas: o arquivo salvo guarda o valor dele.

## 4. SketchUp (memória)

`skp_core.GroupPlan` ganha `parent_path` e `children` (árvore). Contagem de figuras puladas no resultado do plano.
Material importado com `btm_skp_material` e o nome base, sem o prefixo `Layer_`.

## 5. Arquivos do pacote

`caffmob_draw/openings/assets/`:
- `nogueira_cor.jpg`, `nogueira_rugosidade.jpg` (convertidos dos PNG do Codex);
- `previa_porta.png`, `previa_janela.png`.

## 6. Migrações

Nenhuma automática. As caixas antigas ficam com `kind = NONE` até "Atualizar portas e janelas" (RN-04).
