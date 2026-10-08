# Investigation: Barra lateral em 5 seções, sem repetição, conversando com a viewport

> Identificador: `005-barra-lateral-viewport`
> Data: `2026-10-07`
> Fontes: `audit/cross-check.md` da 004, leitura de `caffmob_draw/ui/`, `operators/viewport_hud.py`, menus e RAG 5.2

## 1. O que existe hoje

- **44 painéis** na aba CAFFMob Draw (12 de topo, 32 filhos). Levantamento com o add-on registrado no Blender 5.2:
  - topo: `BTM_PT_environment_builder` (4 abas internas), `BTM_PT_object_properties`, `BTM_PT_nesting_panel`,
    `BTM_PT_collisions`, `HOME_BUILDER_PT_project`, `_room_layout`, `_product_library`, `_layout_views`, `_2d_details`,
    `_annotations`, `_hidden_header` e `HB_FACE_FRAME_PT_active_cabinet`.
  - filhos: 8 em Propriedades, 7 no Face Frame, 7 no Room Layout, 5 em Annotations, 3 em Layout Views e 2 em Project.
- **17 operadores** são desenhados por mais de um painel (inventário estático):
  - paredes, aberturas, teto, luzes e obstáculo: Construtor × Room Layout;
  - ambientes: Configurações × Project › Rooms;
  - abrir frentes: inspeção × Propriedades.
- **Galeria:** o `draw_library_ui` é chamado em `ui/panels.py:251` e em `ui/view3d_sidebar.py:642`.
- **Bibliotecas do usuário:** três (frameless "User", face frame, `customize`).
- **Menu do botão direito:** três inserções independentes em `VIEW3D_MT_object_context_menu`:
  - `ui/menu_apend.py` (submenu `MENU_ID`);
  - `stick/ops_stick.py` (Grudar e Abrir editor);
  - `move_over/insertion_plane.py`.
- **HUD** (`operators/viewport_hud.py`): sem modal persistente, roteia o clique por entradas de keymap. Os widgets
  seguem um protocolo (`visible`, `on_click`, desenho) e as linhas vêm de `_rows()`. Hoje mostra os modos de seleção e
  os modais de agarrar, abrir e Mover Sobre. Vem desligado.

## 2. Alternativas avaliadas

| Tema | Alternativa | Por que ficou ou saiu |
|---|---|---|
| Seções | 5 `Panel` de topo | Saiu: não há API para abrir um `Panel` por código, e Selecionado precisa abrir sozinho |
| Seções | Abas (enum) num painel | Saiu: a Q1 escolheu empilhado |
| Seções | Um `Panel` com `layout.panel_prop` | **Ficou** (D-01): o estado fica numa propriedade nossa |
| Conteúdo legado | Reescrever cada `draw` | Saiu: milhares de linhas e risco de perder função |
| Conteúdo legado | Esconder com `poll` | Saiu: as classes continuariam registradas e apareceriam na busca de menus |
| Conteúdo legado | Proxy que chama o `draw` da classe | **Ficou** (D-04) |
| Testes de interface | Varredura estática | Saiu: não enxerga `poll` nem chamadas indiretas |
| Testes de interface | Camada falsa que imita `UILayout` | **Ficou** (D-11): roda em segundo plano, no código real |
| Prévia do ímã | Mover o objeto durante o arraste | Saiu: brigaria com o G nativo e com o desfazer |
| Prévia do ímã | Desenho `POST_VIEW` da pose calculada | **Ficou** (D-15) |
| HUD ligado | Migrar a preferência para todos | Saiu: a Q4 pediu respeitar a escolha |

## 3. Referências (RAG 5.2)

- `docs/rag/blender-api/corpus/bpy.types.UILayout.md#bpy.types.UILayout.panel_prop`: estado aberto/fechado numa
  propriedade booleana nossa; só em largura total.
- `docs/rag/blender-api/corpus/bpy.types.UILayout.md#bpy.types.UILayout.panel`: estado guardado na região, sem
  controle por código.
- `docs/rag/blender-api/corpus/bpy.types.Window.md#bpy.types.Window.modal_operators`: saber se há movimento em
  andamento (já usado na 004).
- `bpy.msgbus.subscribe_rna`: a assinatura confirmada contra o RAG na codificação (`rag_search.py --symbol`).

## 4. Ótica de design (Impeccable, registro *product*)

- **Earned familiarity:** painéis empilhados e recolhíveis do Blender, nada inventado.
- **Distill:** "se já está em outro lugar, não repita"; uma ação principal por seção; o resto recolhido.
- **Vocabulário consistente:** mesmo rótulo e ícone para a mesma ação no painel, no menu e no HUD.
- **Estados em texto:** desabilitado com motivo, vazio que ensina o próximo passo.
