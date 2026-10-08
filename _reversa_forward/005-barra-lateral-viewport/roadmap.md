# Roadmap: Barra lateral em 5 seções, sem repetição, conversando com a viewport

> Identificador: `005-barra-lateral-viewport`
> Data: `2026-10-07`
> Requirements: `_reversa_forward/005-barra-lateral-viewport/requirements.md`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA

## 1. Resumo da abordagem

Três incrementos, cada um com teste de fumaça e captura da barra lateral:

- **I1. Rede de segurança.** Uma "camada falsa" (`ui/layout_probe.py`) imita o `UILayout` e registra cada operador,
  menu e propriedade que um painel desenha. Com ela, dois testes rodam no Blender em segundo plano:
  - **inventário de capacidade** (RF-08): compara com uma linha de base gravada antes da mudança;
  - **não repetição** (RF-09): nenhum operador pode ser desenhado por duas seções.
  Nenhuma interface muda neste incremento.
- **I2. Navegação única.** Um único `Panel` hospedeiro (`BTM_PT_sidebar`) desenha as 5 seções como painéis de layout
  recolhíveis (`UILayout.panel_prop`), com o estado aberto/fechado em propriedades nossas. É isso que deixa Selecionado
  abrir sozinho. Os painéis legados e os subpainéis atuais deixam de ser registrados na aba. O conteúdo deles é desenhado
  dentro das seções por um "proxy" que chama o `draw` de cada classe com o layout da seção, sem reescrever a lógica das
  bibliotecas.
- **I3. Viewport.**
  - menu do botão direito unificado;
  - terceira linha do HUD com as ações do item selecionado;
  - HUD ligado por padrão;
  - prévia do ímã: um `POST_VIEW` que, durante um movimento modal, desenha a face-alvo e a pose encostada sem mexer no
    objeto.

## 2. Princípios aplicados

`.reversa/principles.md` não existe; valem as regras do `CLAUDE.md` e os princípios do `PRODUCT.md`:

| Princípio | Como a feature se relaciona | Status |
|---|---|---|
| Consultar o RAG 5.2 | `UILayout.panel_prop` (`docs/rag/blender-api/corpus/bpy.types.UILayout.md#bpy.types.UILayout.panel_prop`), `Window.modal_operators` (`.../bpy.types.Window.md#bpy.types.Window.modal_operators`), `bpy.msgbus.subscribe_rna` (a confirmar na codificação) | respeita |
| Handlers removidos em todos os caminhos e no `unregister()` | Assinatura `msgbus` do objeto ativo (refeita no `load_post`), `POST_VIEW` da prévia do ímã, linha nova do HUD | respeita |
| Propriedades por atributo; `# type: ignore` | Estados das seções em `WindowManager.btm_sidebar` | respeita |
| Textos em pt-BR com en-US | Títulos de seção e de grupo, mensagens de estado vazio | respeita |
| `PRODUCT.md`: viewport primeiro, convenções do Blender, cada função num lugar, contextual | São o objetivo da feature (RN-01..RN-10) | respeita |
| Editar só `caffmob_draw/` | As bibliotecas legadas não mudam de lógica; só deixam de registrar painéis na aba | respeita |

## 3. Decisões técnicas

| ID | Decisão | Justificativa | Alternativas descartadas | Confidência |
|----|---------|----------------|--------------------------|-------------|
| D-01 | **Painel hospedeiro único** `BTM_PT_sidebar` (sem cabeçalho) com 5 `layout.panel_prop(state, "open_<seção>")`: Construir, Inserir, Selecionado, Verificar, Produção/Projeto. Os grupos internos também são `panel_prop`. O resultado tem a aparência de painéis empilhados e recolhíveis do Blender | Só `panel_prop` deixa abrir uma seção por código (Selecionado abre sozinho, RN-01). Um `Panel` comum guarda o estado na região, sem API para abrir | 5 `Panel` de topo (não há como abrir Selecionado); manter as abas atuais (Q1 escolheu empilhado) | 🟢 |
| D-02 | **Estado das seções** em `WindowManager.btm_sidebar` (não salvo no arquivo): `open_build`, `open_insert`, `open_selected`, `open_check`, `open_project` e os `open_*` dos grupos. O padrão é tudo recolhido, exceto Construir sem seleção. O Blender lembra o estado durante a sessão | Lembrar o estado sem sujar o arquivo nem o desfazer | `Scene.btm_settings` (marcaria o arquivo como alterado a cada clique) | 🟢 |
| D-03 | **Selecionado abre sozinho**: `bpy.msgbus.subscribe_rna(key=(bpy.types.LayerObjects, "active"))` liga `open_selected` quando o ativo vira um objeto reconhecido. Assinatura refeita no `load_post` e removida no `unregister` | `draw` não pode gravar dados; o msgbus avisa a troca de ativo | Gravar no `draw` (proibido); timer de varredura | 🟡 |
| D-04 | **Proxy de painel** (`ui/sidebar_proxy.py`): `draw_panel(cls, layout, context)` testa `cls.poll(context)` e chama `cls.draw(proxy, context)`. O `proxy` tem `layout` e, para o resto, cai nos atributos da classe, com métodos ligados ao proxy. Os painéis legados (Room Layout e filhos, Project, Layout Views, 2D Details, Annotations, Face Frame Cabinet e filhos) e os subpainéis atuais (personalizar, agregados, elemento filho, colisão) **deixam de ser registrados** como `Panel` e passam a ser desenhados dentro das seções | Preserva a lógica das bibliotecas (RN-03) e evita reescrever ~3 mil linhas de desenho legado | Reescrever cada painel; manter registrados e esconder com `poll` (continuariam aparecendo em outras abas e na busca) | 🟡 (alguns `draw` legados podem usar algo da região; a fumaça desenha todos) |
| D-05 | **Construir** (RN-07, RF-02): uma linha de ação principal ("Desenhar Paredes", "Editor de Paredes"). Depois, grupos recolhidos que reaproveitam os corpos legados pelo proxy: Paredes (padrões), Aberturas, Piso e teto, Obstáculos, Luzes, Escadas, Imagem de referência, Geometrias (Placa/Caixa). Sem parede (`floor_builder.scene_walls`), Aberturas e Piso e teto ficam com `enabled = False` e a linha "Desenhe uma parede primeiro". A grade de botões da aba Construtor atual sai | Fim dos 8 botões repetidos (A003); recupera a regra R-01 da UI | — | 🟢 |
| D-06 | **Inserir** (RN-04, RF-03): o seletor `home_builder.product_tab` e o `draw_library_ui` da biblioteca escolhida, **chamado num lugar só**. O grupo **Meus módulos** junta três origens numa lista com filtro e com a origem indicada: módulos salvos (`customize/library_io`), grupos do usuário do frameless e do face frame. Cada item chama o operador de inserção da própria origem. A seção "User" do frameless e a do face frame deixam de aparecer dentro da galeria (o `draw_library_ui` ganha um parâmetro para omiti-las) | Uma galeria (A001) e uma lista do usuário (A007), sem mudar como cada biblioteca insere | Unificar o formato dos arquivos das três bibliotecas (fora do escopo) | 🟡 |
| D-07 | **Selecionado** (RN-05, RF-04): grupos por tipo, a partir de `selection/classify`. Para módulo, 4 grupos abertos por padrão: **Medidas e cotas** (dimensões, limites, cotas, Abrir editor de armário), **Personalizar** (003), **Posição e vínculo** (posição, rotação, Mover Sobre, plano de inserção, elemento filho) e **Abrir** (frentes). Recolhidos: Agregados e folhas, Colisão do item, Arranjo, Outras/Ações e **Opções do face frame** (os 7 subpainéis legados pelo proxy). Parede, abertura, geometria, obstáculo e piso usam os grupos que `ui/object_properties.py` já desenha por tipo, no máximo 4 abertos | Fim das 8 sobreposições (A008), sem perder nada | — | 🟡 (lista final por tipo fechada no código; lacuna do requirements) |
| D-08 | **Verificar** (RN-06, RF-05): o corpo de `draw_inspection_box` (abrir/fechar tudo, ângulo, interferência) e `collision/panels.draw_collisions`. A chave "Evitar Sobreposição" sai de lá e fica só em Produção/Projeto (A009). O painel de topo "Colisões" deixa de existir | Um lugar para verificar | — | 🟢 |
| D-09 | **Produção/Projeto** (RN-06, RF-06, RF-07): Plano de corte (`draw_cut_plan`, uma vez; sai o painel "Plano de Corte (Nesting)"), Ambientes (o corpo de `HOME_BUILDER_PT_project_rooms`, com reordenar; sai a cópia da aba Configurações), Configurações (unidade, snap, Evitar Sobreposição, padrões, chapa MDF), Projeto (dados do projeto) e **Desenhos 2D** recolhido (Layout Views, 2D Details, Annotations pelo proxy), que some com `hide_2d_drawing_panels` | Fim de A005, A006 e A009; 2D conforme a Q3 | — | 🟢 |
| D-10 | **Ordem e estado vazio**: cada seção começa pela ação principal. Selecionado sem seleção mostra "Selecione um objeto na viewport". Os títulos de seção e grupo usam um vocabulário fixo (mesmo rótulo e ícone em painel, menu e HUD), centralizado em `ui/sidebar_vocab.py` | Consistência (RNF) | — | 🟢 |
| D-11 | **Camada falsa** `ui/layout_probe.py`: classe que imita `UILayout` (`row`, `column`, `box`, `split`, `grid_flow`, `panel_prop` devolvendo corpo aberto, `operator` devolvendo um objeto que aceita atributos, `prop`, `menu`, `label`, `template_*`…) e registra os `bl_idname` dos operadores com o painel ou seção de origem. Os testes desenham a barra lateral em contextos fixos (sem seleção; com parede; com balcão frameless, face frame, closets, módulo `btm`; com geometria; com item grudado), com todos os `panel_prop` forçados abertos | Teste em segundo plano, sem janela, cobrindo o código de desenho real | Varredura estática do código (não vê `poll` nem chamadas indiretas) | 🟢 |
| D-12 | **Linha de base** `tests/fixtures/sidebar_inventory_baseline.json`, gravada **antes** de I2 com a camada falsa sobre os painéis atuais. O teste de inventário (RF-08) aceita o operador num painel, no menu de contexto ou no HUD. O de não repetição (RF-09) conta só a barra lateral | Prova RN-03 e RN-02 | — | 🟢 |
| D-13 | **Menu do botão direito unificado** (`ui/context_menu.py`, RF-13): uma só função prependida a `VIEW3D_MT_object_context_menu`. Mostra o submenu do objeto (`MENU_ID`, como hoje) e as ações frequentes do tipo: módulo e geometria ganham Grudar ou Desgrudar e Mover no plano, Mover Sobre, Abrir editor de armário, Verificar colisões do item e Abrir/Fechar frentes; parede fica só com as da parede; todos ganham "Usar como plano de inserção". Saem as três inserções separadas de hoje (`ui/menu_apend.py`, `stick/ops_stick.draw_context_menu`, `move_over/insertion_plane._menu`) | Um caminho de contexto só, previsível | — | 🟢 |
| D-14 | **HUD** (RF-11, RF-12): `use_viewport_hud` passa a ter padrão `True`. Quem salvou as preferências com o HUD desligado mantém o valor salvo; quem nunca mexeu passa a ver o HUD. O HUD ganha uma terceira linha de `_ItemActionButton`: até 4 ações do item ativo (as primeiras de D-13: Grudar/Desgrudar, Mover Sobre, Abrir editor de armário, Verificar colisões), com o mesmo rótulo de `sidebar_vocab`. A linha dos modos continua | O HUD já tem o protocolo de widget e roteamento de clique (`operators/viewport_hud.py`) | HUD novo | 🟡 (o Blender não distingue "nunca mexeu" de "escolheu o padrão antigo") |
| D-15 | **Prévia do ímã** (RF-14, RF-15): `stick/magnet_preview.py` com um `POST_VIEW` (e `POST_PIXEL` para o nome do hospedeiro) que só desenha quando um movimento modal está rodando (`stick/settle.is_move_operator`) e o ímã está ligado. O item é o ativo (ou a prévia do `PlacementMixin`, lida da instância do modal). Uma função pura nova, `magnet.preview_pose(item, hit)`, calcula a matriz encostada (mesma orientação de `link.orient`, mesmo deslocamento de `frame.shift`) **sem alterar o objeto**. O desenho mostra o contorno do polígono da face e a caixa do item na pose encostada. Não há prévia quando o item está numa parede da biblioteca | Atende o RF-12 da 004 sem tocar nos modais; a prévia é só desenho e some sozinha ao fim do modal | Mover o objeto de verdade durante o arraste (brigaria com o G nativo) | 🟡 (custo do raycast por quadro medido na fumaça) |
| D-16 | **Código morto** (RF-10): `build.py` deixa de incluir `catalog/`. A pasta fica no repositório, documentada como não usada | Limpeza sem efeito visível; não apaga trabalho | Apagar a pasta | 🟢 |

## 4. Premissas

Nenhum `[DÚVIDA]` aberto. Premissas técnicas:

| Premissa | Origem | Risco se errada |
|---|---|---|
| Os `draw` dos painéis legados usam só `self.layout` e atributos da classe | D-04 | Um painel que dependa de `self.bl_rna` ou de algo da região falha no proxy; correção pontual nele, coberta pela fumaça que desenha todos |
| `panel_prop` aninhado dentro do corpo de outro `panel_prop` funciona em largura total | D-01 | Grupos internos viram cabeçalhos com `prop(toggle)` em vez de layout panels |
| A assinatura `msgbus` no ativo dispara ao clicar na viewport e ao trocar pelo Outliner | D-03 | Selecionado não abre sozinho em algum caminho; fallback: abrir no primeiro desenho via timer |

## 5. Delta arquitetural

| Componente | Arquivo de origem no legado | Tipo de mudança | Resumo |
|------------|------------------------------|-----------------|--------|
| Barra lateral (UI) | `_reversa_sdd/ui/requirements.md` (RF-01, R-01, R-02) | regra-alterada | Um painel hospedeiro com 5 seções; R-01 (sem parede) volta a valer em Construir |
| Painel com abas | `ui/panels.py` (`BTM_PT_EnvironmentBuilder`, `BTM_PT_NestingPanel`) | componente-extinto | Conteúdo redistribuído nas seções |
| Painéis legados Home Builder | `ui/view3d_sidebar.py` | regra-alterada | Classes ficam, não registram na aba; corpos desenhados pelo proxy |
| Painel do face frame | `product_libraries/face_frame/ui_face_frame.py` | regra-alterada | Vira grupo recolhido em Selecionado |
| Propriedades do objeto | `ui/object_properties.py` (002 D-10, 003 D-25) | regra-alterada | Grupos por tipo, no máximo 4 abertos |
| Subpainéis 003/004 | `customize/panels.py`, `aggregates/panels.py`, `stick/panels.py`, `collision/panels.py` | regra-alterada | Desenhados como grupos; "Biblioteca de módulos" vai para Inserir › Meus módulos |
| Galerias das bibliotecas | `props_hb_frameless.draw_library_ui`, `props_hb_face_frame.draw_library_ui`, `props_closets.draw_library_ui` | regra-alterada | Parâmetro para omitir a seção do usuário |
| Menu de contexto | `ui/menu_apend.py`, `stick/ops_stick.py`, `move_over/insertion_plane.py` | regra-alterada | Uma entrada unificada (`ui/context_menu.py`) |
| HUD | `operators/viewport_hud.py` | regra-alterada | Ligado por padrão; linha de ações do item |
| Ímã | `stick/magnet.py` | regra-alterada | `preview_pose` puro; prévia `POST_VIEW` durante o arraste |
| Empacotamento | `build.py` | regra-alterada | Sem `catalog/` |
| Testes | `tests/` | componente-novo | Camada falsa, inventário e não repetição |

## 6. Delta no modelo de dados

- Novo `WindowManager.btm_sidebar` (estados das seções e grupos, filtro de Meus módulos; não salvo). A preferência
  `use_viewport_hud` muda o padrão para `True`. Nenhum dado de projeto muda.
- Detalhe completo em: `_reversa_forward/005-barra-lateral-viewport/data-delta.md`

## 7. Delta de contratos externos

Nenhum.

## 8. Plano de migração

1. Gravar a linha de base do inventário (D-12) antes de qualquer mudança de interface.
2. Preferência do HUD: sem migração ativa (D-14). O valor salvo pelo usuário é respeitado.
3. Arquivos de projeto não mudam.

## 9. Riscos e mitigações

| Risco | Impacto | Probabilidade | Mitigação |
|-------|---------|---------------|-----------|
| Alguma ação some na reorganização | alto | médio | Teste de inventário contra a linha de base (D-12), obrigatório antes de fechar I2 |
| `draw` legado falha no proxy | médio | médio | Fumaça desenha todas as seções com todos os grupos abertos nos 8 contextos; erro de desenho falha o teste |
| Barra lateral lenta por desenhar tudo num painel | médio | baixo | Corpos recolhidos não são desenhados (`panel_prop` devolve `None`); meta de 16 ms medida |
| Prévia do ímã pesa no arraste | médio | médio | Raycast só do item ativo, com cache por quadro; desliga quando o ímã está desligado |
| Usuário acostumado com as abas antigas | baixo | alto | Mesma ordem do trabalho; guia do usuário atualizado; nenhuma ação removida |

## 10. Critério de pronto

- [ ] Todas as ações do `actions.md` marcadas `[X]`
- [ ] Testes de inventário e de não repetição passando; fumaça por incremento com captura da barra lateral
- [ ] `ruff check caffmob_draw/`, `python3 docs/rag/tools/check_api.py`, `tests/test_i18n_coverage.py` e todas as fumaças existentes sem erro
- [ ] `cross-check.md` (se executado) sem CRITICAL nem HIGH
- [ ] `regression-watch.md` gerado

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-10-07 | Versão inicial gerada por `/reversa-plan` | reversa |
