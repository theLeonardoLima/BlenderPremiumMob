# Investigation: 006-editor-armario-abas

> Data: `2026-10-08`. Fonte: leitura do código em `caffmob_draw/` (caminhos relativos a ele).

## 1. Editor atual (004)

- Painéis no Image Editor, categoria "Editor de Armário". A ordem é Medidas, Componentes, Personalizar, Mensagens,
  Ajustes automáticos e Confirmar (`cabinet_editor/panels.py`).
- Os botões só fazem `Session.push`. Quem edita é o modal `caffmob.cabinet_editor_modal` (`UNDO`), e por isso o
  Confirmar gera um único passo de desfazer (`cabinet_editor/ops_editor.py`).
- O rascunho é uma pilha de `EditorState(dimensions, spec)`, comparada pela `signature` (`cabinet_editor/state.py`).
- O clique na vista frontal seleciona uma peça (`elevation.hit`). Hoje a área vazia não seleciona nada.

## 2. Peças da caixa por biblioteca

| Biblioteca | Peças | Espessura | Esconder/remover existente |
|---|---|---|---|
| Frameless | Objetos separados por nome: Left/Right Side, Bottom, Top, Back, Toe Kick, travessas (`product_libraries/frameless/types_frameless.py:125-313`) | Uma só, `'Material Thickness'` da raiz, por driver (`:16-18`) | Só `'Remove Bottom'` (`:35`), que esconde Bottom e Toe Kick, alonga o fundo e baixa o bay. `'Base Top Construction'` esconde o tampo |
| Face frame | Objetos por `hb_part_role`, refeitos pelo `recalculate()` (`types_face_frame.py:1892-2112`) | `material_thickness`, `back_thickness`, `division_thickness` por armário (`props_hb_face_frame.py:4938-4959`) | `remove_bottom` e `remove_carcass` por bay (`:5610`, `:5614`) |
| Closets | Painéis `CLOSET_PANEL` 0..N (o primeiro e o último são as laterais), fundo e tampo por bay (`types_closets.py:44-78, 300-404`) | Só da cena (`panel_thickness`, `shelf_thickness`) | `remove_bottom` e `remove_cleat` por bay (`props_closets.py:209-212`) |
| `btm` | Uma malha só (`geometry/mesh_gen.py:246-306`) | `thickness` único (`data/properties.py:287`) | Nenhum |

## 3. Interior e divisões existentes

- **Frameless:** `InteriorSplitterVertical/Horizontal` ocupam a seção inteira, **sem recuo** (`types_frameless.py:2127-2139`).
  As prateleiras têm `'Shelf Setback'` (`:1222-1264`).
- **Face frame:** a árvore de splits (`solver_face_frame.py:4186-4334`) gera divisões de região inteira, sem recuo.
  O adaptador cria uma divisória só e ignora alturas (`customize/adapters/face_frame.py:134-167`).
- **Closets:** cubbies verticais de largura igual, sem recuo. O adaptador recusa divisória (`customize/adapters/closets.py:111`).
- **`btm`:** só prateleiras, com recuo fixo de 20 mm (`mesh_gen.py:241`).

Conclusão: nenhuma biblioteca oferece "chapa num subvão escolhido, com recuo na frente e atrás". Por isso o motor é
nosso (D-03, D-04).

## 4. Plano de corte

- Peça = descendente com modificador `GeoNodeCutpart`, visível (`cutting/part_sources.py:104-108, 132-159`), e
  classificada pelo nome ou pelo papel (`cutting/part_roles.py:142-227`).
- Material, fitas e limites vêm do padrão por linha e componente (`cutting/part_extractor.py:44-69`).
- Módulos `btm` usam uma lista sintética fixa (`part_sources.py:178-216`).
- **Face frame não entra no plano de corte** (`part_sources.py:17-18, 74-90`).

## 5. Alternativas avaliadas

| Alternativa | Por que não |
|---|---|
| Usar o interior de cada biblioteca para a Divisão | Quatro implementações diferentes, nenhuma com recuo; o closets nem tem divisória |
| Agregado da 003 como divisão | O agregado prende-se a uma face **externa** do pai e não ocupa um vão (`aggregates/limits.py:1-8`) |
| Estender e Reduzir genéricos (mover peças vizinhas) | Drivers (frameless) e solver (face frame, closets) desfazem no próximo recálculo |
| Divisões por drivers | Subvão aninhado vira expressão longa e frágil. O reposicionamento em Python (D-10) é mais simples e testável |

## 6. Referências da API (RAG 5.2)

- `UILayout.prop_tabs_enum`: `docs/rag/blender-api/corpus/bpy.types.UILayout.md#bpy.types.UILayout.prop_tabs_enum`
- A confirmar na codificação com `rag_search.py`: `bpy.app.handlers.depsgraph_update_post`, `Object.driver_add`,
  `FCurve.driver.expression`, `Driver.variables.new`.
