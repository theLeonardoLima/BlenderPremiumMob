# Roadmap: Editor de armário, grudar em superfície plana e colisão

> Identificador: `004-editor-armario-grudar`
> Data: `2026-10-07`
> Requirements: `_reversa_forward/004-editor-armario-grudar/requirements.md`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA

## 1. Resumo da abordagem

Três incrementos em sequência, cada um com teste de fumaça próprio, na ordem do requirements §8 (B → C → A):

- **I1. Grudar (`stick/`):** vínculo gravado no item (`Object.btm_stick`) com o hospedeiro, a face e a posição no
  plano dela. Um handler de depsgraph mantém o item encostado quando o hospedeiro muda (inclusive a espessura da parede,
  defeito confirmado hoje) e devolve ao plano o que for movido para fora dele. Comando "Grudar", ímã no
  posicionamento do plugin, desgrudar, vínculo perdido e migração automática dos módulos que já estão na parede.
- **I2. Colisão de corpo (`collision/`):** regras puras (pares que não contam, tolerância, ordem, profundidade) e uma
  varredura no Blender que reaproveita o pré-filtro por caixa + `BVHTree.overlap` de `inspection/interference.py`.
  Painel com "Ir para", destaque na viewport, marca de desatualizado, aviso ao soltar e ao salvar.
- **I3. Editor de armário (`cabinet_editor/`):** janela própria no mesmo molde do editor de paredes (`walls2d/window.py`):
  vista frontal desenhada em `POST_PIXEL`, lista de componentes, campos de medida e as edições da 003 pelos
  adaptadores de `customize/`. Diferente das paredes, o módulo é editado **ao vivo** e o rascunho é um conjunto de
  instantâneos (medidas + `spec`) que permite desfazer dentro do editor e cancelar reaplicando o instantâneo inicial.

Como nas features anteriores, a matemática fica em Python puro testável com `unittest`, e a camada do Blender é fina
por cima.

## 2. Princípios aplicados

`.reversa/principles.md` não existe; valem as regras do `CLAUDE.md`:

| Princípio (CLAUDE.md) | Como a feature se relaciona | Status |
|---|---|---|
| Editar só `caffmob_draw/`; consultar o RAG 5.2 | APIs a usar já confirmadas: `BVHTree.overlap` (`docs/rag/blender-api/corpus/mathutils.bvhtree.md#mathutils.bvhtree.BVHTree.overlap`), `bpy.ops.view3d.view_selected` (`docs/rag/blender-api/corpus/bpy.ops.view3d.md#bpy.ops.view3d.view_selected`), `Scene.ray_cast` (já usado em `move_over/insertion_plane.py`) | respeita |
| Operadores que alteram dados com `UNDO` | Grudar, desgrudar, mover grudado, "Afastar até encostar" e Confirmar do editor: um passo cada. Os botões internos do editor **não** têm `UNDO` (D-17) | respeita |
| Handlers removidos em todos os caminhos e no `unregister()` | `depsgraph_update_post` do grudar (D-04) e da colisão (D-12), `load_post` da migração (D-08), `save_post` do aviso (D-15), `POST_VIEW`/`POST_PIXEL` do destaque (D-13) e da janela do editor (D-16), keymap do apagar (D-07) | respeita |
| Inputs de GN só via `compat` | Espessura e comprimento da parede lidos por `GeoNodeWall.get_input` (que já passa por `compat`) | respeita |
| Propriedades por atributo | Dados novos em `PropertyGroup` (`btm_stick`, preferências, estado da colisão e do editor) | respeita |
| Textos em português, com tradução pt_BR/en_US | Todo texto novo entra em `data/translations/*.json`; texto desenhado usa `tr()`/`N_()` (`data/i18n.py`) | respeita |

## 3. Decisões técnicas

**I1. Grudar**

| ID | Decisão | Justificativa | Alternativas descartadas | Confidência |
|----|---------|----------------|--------------------------|-------------|
| D-01 | **Núcleo puro `stick/frame.py`:** referencial da face no espaço local do hospedeiro, conversão posição do item ↔ (`u`, `v`, `distance`, `spin`), projeção de um ponto no plano, teste "item fora da face", teste de face plana (vértices a ≤ 0,5 mm do plano). Reaproveita `aggregates/limits.face_axes`, `box_for` e `params_from_box` **sem** o clamp de contorno | Matemática é o maior risco; mesmo padrão de `aggregates/limits.py` (003 D-01) | Lógica nos operadores | 🟢 |
| D-02 | **Dois tipos de face:** `BOX_SIDE` (um dos seis lados ±X/±Y/±Z da caixa local avaliada do hospedeiro: segue mudança de medida) e `PLANE` (plano fixo no referencial local do hospedeiro, para face inclinada de malha qualquer: segue mover/girar, não segue medida). Ao grudar, se a normal da face clicada coincide (≤ 1°) com um lado da caixa e o ponto está nesse lado (≤ 0,5 mm), usa `BOX_SIDE`; senão `PLANE` | Paredes, painéis, módulos e geometrias são caixas; índice de polígono muda quando o GN reavalia | Guardar o índice do polígono do `ray_cast` | 🟢 |
| D-03 | **Vínculo = parentesco Blender + `btm_stick`:** o item vira filho do hospedeiro (inversa identidade, como `aggregates/convert.py:33`) e `btm_stick` guarda o resto. Mover/girar/apagar o hospedeiro já leva o item | Mesmo caminho da 003 e do posicionamento na parede | Constraint `CHILD_OF` | 🟢 |
| D-04 | **Handler `depsgraph_update_post` (`@persistent`) em `stick/apply.py`:** (a) quando a caixa avaliada de um hospedeiro muda, reposiciona os itens grudados a partir de `u/v/distance` (cobre espessura e comprimento da parede, D-09); (b) quando um item grudado é movido (inclusive pelo G nativo), projeta a nova posição no plano da face, recalcula `u/v` e restaura `distance`/`spin`. Grava só quando o valor muda (evita laço) e guarda a matriz de mundo do item (`last_world`) a cada aplicação | O G nativo não tem gancho (nada em `transform.translate`); o padrão já existe em `aggregates/apply.py:80-104` | Gancho só nos operadores do plugin (G nativo tiraria o item da face) | 🟡 (custo e laço medidos na fumaça) |
| D-05 | **Comando "Grudar" (`caffmob.stick_to_face`):** modal com o item selecionado; o clique faz `Scene.ray_cast` excluindo o item, valida a face (D-01), gira o item para a normal, encosta o lado de trás da caixa e grava o vínculo (`UNDO`). Também no menu de contexto e no painel de propriedades | Mesmo raycast de `move_over/insertion_plane.py:46` | Seleção de dois objetos (não diz qual face) | 🟢 |
| D-06 | **Ímã (RF-12, RN-10a):** `BTM_AddonPreferences` ganha `stick_magnet` (Bool, padrão ligado) e `stick_magnet_distance` (Float, `LENGTH`, padrão 50 mm, 1-500 mm). No posicionamento do plugin (`hb_placement.PlacementMixin.update_snap` → `hb_snap.best_hit`, que passa a devolver a normal), quando o ponto acertado está numa face plana a até a distância, a prévia gira para a normal e encosta; confirmar grava o vínculo. O "Mover" do item grudado (D-07) usa o mesmo ímã para trocar de face | Todas as bibliotecas passam pelo `PlacementMixin`; preferência vale para todos os arquivos (Q3) | Ímã no G nativo (sem gancho); propriedade de cena (valeria só no arquivo) | 🟡 (as bibliotecas que já prendem à parede mantêm a regra delas; o ímã atua só fora da parede) |
| D-07 | **Mover, desgrudar e apagar:** `caffmob.stick_move` (modal restrito ao plano, matemática do modal de `aggregates/ops_aggregate.py:130-196` sem clamp); `caffmob.stick_release` volta o parentesco anterior e mantém a matriz de mundo. O override de apagar de `aggregates/ops_aggregate.py:199-262` passa a tratar também filhos grudados: antes de apagar o hospedeiro, solta cada um no lugar e avisa "Vínculo perdido: <item>" | Um override só para X/Delete; evita salto de posição quando o pai some | Segundo keymap de apagar | 🟢 |
| D-08 | **Migração (RN-10, RF-19):** função `stick.migrate.run(scene)` chamada no `load_file_post` já existente (`__init__.py:69-94`, ao lado de `standards.migration.run`): para cada módulo raiz filho de `GeoNodeWall` sem `btm_stick`, grava `BOX_SIDE` `NEG_Y` (frente, Y local ≈ 0) ou `POS_Y` (trás, Y local ≈ espessura, giro de 180°) pela mesma regra de `measure/scene_cotas.py:43-46`, `distance` = recuo atual (negativo quando o produto entra na parede, face frame `recess`). Idempotente; marca a cena com `btm_settings.stick_migrated` | Arquivos antigos não registram o lado (nenhum idprop); a regra de lado já existe nas cotas | Perguntar ao abrir (Q5 escolheu automático) | 🟢 |
| D-09 | **Parede:** as faces são `NEG_Y` (Y = 0, "frente", lado onde o posicionamento põe os módulos) e `POS_Y` (Y = espessura, "trás"), nomes da interface "frente"/"trás" seguindo `ops_placement.py`. Com D-04, mudar a espessura no editor de paredes, no painel ou por tipo (`operators/walls.py:4300-4335`) mantém os módulos de trás encostados sem tocar em `walls2d/apply.py` | Hoje só a face Y = espessura se move e nada acompanha (mapeamento §2); o legado chama Y = 0 de "back" em `walls.py:1192`, por isso o nome fica só na interface do plugin | Corrigir em cada lugar que muda espessura | 🟢 |
| D-10 | **Avisos sem operador (RN-08, RN-08a):** handlers não podem usar `self.report`; os avisos "Vínculo perdido" e "Item fora da face" vão para a barra de status pelo mesmo mecanismo de `ui/save_feedback.py:27-39` e para o console. O estado `out_of_face` fica gravado em `btm_stick` e o painel do item mostra o aviso enquanto valer | Padrão já usado no aviso de salvar (003 D-27) | Pop-up modal em handler (não permitido) | 🟢 |
| D-11 | **Hospedeiro na interface:** o item mostra "Elemento filho de: <nome do objeto> — <face>"; o hospedeiro mostra a lista "Elementos filhos" com os itens grudados. Sem a palavra "pai", para não confundir com o agregado da 003 | Lacuna do requirements §10 | "Elemento pai" | 🟡 |

**I2. Colisão**

| ID | Decisão | Justificativa | Alternativas descartadas | Confidência |
|----|---------|----------------|--------------------------|-------------|
| D-12 | **Núcleo puro `collision/rules.py`:** dados de entrada = lista de itens (nome, tipo, caixa orientada no mundo, raiz, pai de agregado, hospedeiro de grudado, abertura→parede, `collision_override`); saída = pares candidatos (RN-12 aplicada), profundidade pela sobreposição das caixas orientadas no referencial do item (mínimo dos três eixos), classificação (contato ≤ 1 mm, colisão, penetração em parede/obstáculo, piso/teto) e ordenação estável (RN-13). Um par gera uma ocorrência | Testável sem Blender; profundidade exata para móveis em caixa, que são a maioria | Profundidade por malha (cara e instável) | 🟢 |
| D-13 | **Varredura no Blender `collision/scan.py`:** itens = `classify.movable_root` (módulos, geometrias, obstáculos), eletrodomésticos (`hb_utils.get_appliance_bp`), agregados (`btm_aggregate.is_aggregate`), portas/janelas de ambiente; estáticos = paredes (`floor_builder.scene_walls`), piso e teto (`IS_FLOOR_BP`, `IS_CEILING_BP`). Ignora `IS_CUTTING_OBJ`, `IS_2D_ANNOTATION`, `IS_DIMENSION`, `WIRE`/`BOUNDS`, ocultos. Para cada par que o núcleo aceita, confirma com `BVHTree.overlap` das malhas avaliadas (cache de BVH como `inspection/interference._Targets`), o que respeita os furos de porta/janela na parede | Reaproveita o teste fino da 001; caixa sozinha daria falsa colisão no vão de uma porta | Só caixa; física do Blender | 🟡 (2 s com 200 módulos medido na fumaça) |
| D-14 | **Estado e painel:** `WindowManager.btm_collision` (lista de ocorrências: tipo, item A, item B, profundidade, ponto; `checked`, `stale`, `error`), não salvo no arquivo como a interferência (`inspection/props.py`). Painel "Colisões" com os estados nunca verificado / desatualizado / sem colisões / erro / lista; "Ir para" seleciona os dois e chama `view3d.view_selected` em `temp_override` na área 3D | Mesmo modelo de `BTM_PG_InspectionState`; o goto atual só desloca a vista, o requirements pede enquadrar | Gravar no `.blend` | 🟢 |
| D-15 | **Desatualizado e salvar:** `depsgraph_update_post` marca `stale` quando um item da última verificação muda de transformação ou geometria (padrão de `cutting/stale.py:60`). `save_post` mostra na barra de status "N colisões pendentes" quando há ocorrências e o resultado está em dia; com resultado desatualizado, "Colisões não verificadas desde a última mudança". Nunca bloqueia (RN-15) | Mesmo canal de `ui/save_feedback.py` | Verificar a cena inteira no `save_pre` (atrasaria o salvar) | 🟡 |
| D-16 | **Aviso ao soltar (RF-23):** função `collision.check_item(root)` que testa só os vizinhos cuja caixa toca a do item; chamada no fim dos movimentos do plugin: confirmar do `PlacementMixin`, "Mover na Parede" (`move_over/ops_move_on_wall.py:73`), mover agregado e mover grudado. Resultado no relatório ("Colide com <outro>") e no destaque; o item fica onde foi solto (Q2). O Mover Sobre mantém a confirmação dupla que já tem (`move_over/ops_dialog.py:286-297`). No G nativo o resultado fica desatualizado (D-15), sem aviso imediato | Só há gancho nos movimentos do plugin | Temporizador que adivinha o fim do G nativo (frágil) | 🟡 |
| D-17 | **Destaque (RF-22):** `POST_VIEW` com o contorno da caixa dos itens em colisão e `POST_PIXEL` com o rótulo de texto do tipo, no molde de `aggregates/overlay.py` (`_box_lines`, rótulo com sombra); handler ligado enquanto houver ocorrências e removido ao limpar e no `unregister` | Texto, não só cor (RNF de usabilidade) | Trocar material dos objetos | 🟢 |
| D-18 | **Exceções (RF-24):** `btm_plane.collision_override` (Herdar/Ativa/Desativada, hoje sem uso, `data/properties.py:202`) passa a valer na varredura. Chave global = `btm_settings.collision_global` ("Evitar Sobreposição", já usada por `hb_placement.avoid_overlap`): desligada, a verificação não roda e o painel diz "Colisão desligada" | Reaproveita os dois campos existentes | Campo global novo (duas chaves para a mesma ideia) | 🟡 |
| D-19 | **"Afastar até encostar" (RF-26, Could):** desloca o item pelo eixo de menor sobreposição (D-12), para o lado de fora; item grudado só desloca no plano da face; um passo de desfazer | Usa o dado que o núcleo já calcula | Resolver vários pares de uma vez | 🟡 |

**I3. Editor de armário**

| ID | Decisão | Justificativa | Alternativas descartadas | Confidência |
|----|---------|----------------|--------------------------|-------------|
| D-20 | **Janela no molde do editor de paredes:** `caffmob.cabinet_editor` abre uma janela nova com `area_dupli` transformada em `IMAGE_EDITOR` sem imagem (`walls2d/window.py:58-113`), um `draw_handler_add` `POST_PIXEL` global que desenha só na área do editor, o modal `caffmob.cabinet_editor_modal` com `{'REGISTER','UNDO','INTERNAL'}` e painéis na categoria "Editor de Armário". O código comum de janela (abrir, focar a aba, fechar depois, `is_editor_area`) sai de `walls2d/window.py` para `canvas2d/window.py`, usado pelos dois editores | Padrão testado; Q1 pediu tela própria | Painel lateral ampliado | 🟢 |
| D-21 | **Edição ao vivo + instantâneos:** cada edição do editor aplica no módulo real (pelos adaptadores de `customize/` e pelo `selection/editing.set_dimension`), então a vista frontal mostra o resultado verdadeiro de cada biblioteca. O rascunho é uma pilha de instantâneos `EditorState` (medidas + `spec`) num `History` genérico (o de `walls2d/history.py`, que passa a receber a função de assinatura). Desfazer/refazer no editor reaplica o instantâneo; Cancelar reaplica o instantâneo inicial e devolve `CANCELLED`; Confirmar devolve `FINISHED` e o Blender cria **um** passo de desfazer | O módulo não tem modelo puro equivalente ao `WallPlan`; reaplicar pelo adaptador é o caminho que as quatro bibliotecas já suportam | Duplicar o módulo e trocar (quebra nomes, drivers e o vínculo com a parede); `ed.undo_history` dentro do modal (frágil) | 🟡 |
| D-22 | **Botões do editor sem `UNDO`:** as ações dentro do editor são operadores `INTERNAL` sem `UNDO` que só registram um pedido na sessão; o modal executa a edição. As funções dos adaptadores são chamadas direto, sem `bpy.ops` aninhado, onde possível; onde o adaptador usa `run_operator` (operador da biblioteca com `UNDO`), a fumaça confere que nenhum passo extra entra na pilha do Blender | Um passo só no Confirmar (RN-01) | Chamar os operadores `caffmob.customize_*` da 003 (cada um criaria um passo) | 🔴 (comportamento de undo de `bpy.ops` aninhado num modal, a confirmar na fumaça) |
| D-23 | **Vista frontal e componentes (`cabinet_editor/elevation.py`, puro):** para cada objeto filho da raiz, a caixa avaliada levada ao referencial local da raiz (`root.matrix_world.inverted() @ obj.matrix_world`) e projetada em (x, z); tipos pelas regras de `part_roles.classify`, frentes `IS_CABINET_FRONT` e vãos dos adaptadores. A lista de componentes e a vista usam o mesmo nome de objeto como identidade | Nenhum código calcula a elevação por peça hoje (mapeamento §4); as caixas por peça já são lidas assim em `move_over/scene._local_box` | Desenhar a malha | 🟢 |
| D-24 | **Validação (`cabinet_editor/validate.py`, puro):** mensagens `{code, severity, component, parameter, value, range, action, blocks}`. Regras: `DIM-001..003` (vazio, não numérico, fora da faixa); faixa = `editing.LIMITS` (geral) estreitada pelos limites próprios da biblioteca quando existem (`btm_cabinet`, mínimo de porta do estilo da 003 RN-03); `GEO-001` componente fora do volume (caixa da peça além da caixa da raiz + 1 mm); `GEO-002` peças internas sobrepostas (núcleo da colisão, D-12, no referencial da raiz, excluindo pares estruturais que se tocam); `CAT-001` seção sem suporte (`capabilities` da 003). Erro bloqueia Confirmar | Requirements RN-03; reaproveita o núcleo de I2 | Validar só no Confirmar | 🟡 |
| D-25 | **Ajustes automáticos (RF-07):** depois de cada edição, `elevation` antes × depois dá a lista de peças que mudaram de caixa sem serem o alvo da edição, que entraram ou que saíram; a lista fica na sessão e aparece no painel antes de Confirmar | Diferença verificável sem conhecer o motor de cada biblioteca | Pedir a cada adaptador que relate o que mudou | 🟢 |
| D-26 | **Fechar com pendências (RN-04):** o botão "Fechar" do painel pergunta continuar/descartar/confirmar (`invoke_props_dialog` com três opções). Se o usuário fechar a janela do sistema, o modal detecta a janela sumida, reaplica o instantâneo inicial e avisa na barra de status "Editor fechado: alterações descartadas" | A janela do sistema fecha sem passar pelo plugin | Confirmar ao fechar a janela (aplicaria sem pedido) | 🟡 |
| D-27 | **Entrada:** botão "Abrir editor de armário" na caixa de dimensões do painel de propriedades (`ui/object_properties.py:174-186`, mesmo padrão do botão do editor de paredes em `:236-237`) e no menu de contexto do módulo; indisponível sem módulo, com o motivo. "Salvar como módulo" do editor chama `customize/library_io` com o estado atual | Reaproveita a classificação `selection/classify` | Item de menu só | 🟢 |

## 4. Premissas

Nenhum `[DÚVIDA]` aberto no requirements. Premissas técnicas a confirmar durante a codificação:

| Premissa | Origem | Risco se errada |
|---|---|---|
| Operadores das bibliotecas chamados por `run_operator` dentro do modal do editor não criam passos de desfazer próprios | D-22 | Ctrl+Z depois do Confirmar desfaria uma edição por vez; mitigação: chamar as funções das bibliotecas sem `bpy.ops` ou empacotar com `ed.undo_push` controlado |
| Reaplicar o instantâneo (medidas + `spec`) devolve o módulo ao estado inicial nas quatro bibliotecas | D-21 | Cancelar deixaria resíduos; a fumaça compara a elevação antes de abrir e depois de cancelar |
| O handler de grudar (D-04) não entra em laço com o handler dos agregados nem com o recálculo das bibliotecas | D-04 | Cena travando; grava só quando muda e ignora atualizações que ele mesmo causou |
| O ímã cabe no `PlacementMixin` sem mudar a regra de parede das bibliotecas | D-06 | Ímã fica só no "Grudar" e no "Mover" do item grudado; o RF-12 é Should |

## 5. Delta arquitetural

| Componente | Arquivo de origem no legado | Tipo de mudança | Resumo |
|------------|------------------------------|-----------------|--------|
| Grudar (`stick/`) | — | componente-novo | `frame.py` puro, `props.py`, `apply.py` (handler), `ops_stick.py`, `migrate.py`, painel |
| Colisão (`collision/`) | — | componente-novo | `rules.py` puro, `scan.py`, `props.py`, `ops_collision.py`, `overlay.py`, `stale.py`, painel |
| Editor de armário (`cabinet_editor/`) | — | componente-novo | janela, modal, sessão com instantâneos, `elevation.py` e `validate.py` puros, painéis |
| Janela 2D comum | `walls2d/window.py` | regra-alterada | Abrir/focar/fechar extraídos para `canvas2d/window.py`; editor de paredes passa a usar o comum, sem mudança visível |
| Histórico de rascunho | `walls2d/history.py` | regra-alterada | Recebe a função de assinatura; o editor de paredes continua com `plan_signature` |
| Posicionamento | `_reversa_sdd/hb_placement/requirements.md#Requisitos Funcionais` (RF-02, RF-04) | regra-alterada | `hb_snap.best_hit` devolve a normal; ímã de face plana no `PlacementMixin`; aviso de colisão ao confirmar |
| Agregados (apagar) | `aggregates/ops_aggregate.py:199-262` | regra-alterada | Override de apagar também solta filhos grudados no lugar |
| Paredes ↔ módulos | `walls2d/apply.py`, `operators/walls.py` (espessura) | regra-alterada (sem editar esses arquivos) | Módulos grudados acompanham a face pela D-04 |
| Mover na Parede | `move_over/ops_move_on_wall.py` | regra-alterada | Chama o aviso de colisão ao confirmar |
| Preferências | `__init__.py:106` `BTM_AddonPreferences` | regra-alterada | `stick_magnet`, `stick_magnet_distance` |
| Abrir arquivo | `__init__.py:69-94` `load_file_post` | regra-alterada | Chama a migração de grudados |
| Painel de propriedades | `ui/object_properties.py` | regra-alterada | "Elemento filho de", "Elementos filhos", Grudar/Desgrudar, "Abrir editor de armário", "Colisão" por item |

## 6. Delta no modelo de dados

- Novos: `Object.btm_stick`, `WindowManager.btm_collision`, `WindowManager.btm_cabinet_editor` (estado da janela, não
  salvo), duas preferências do add-on e `btm_settings.stick_migrated`. Passam a ser lidos: `btm_plane.collision_override`
  e `btm_settings.collision_global`. Migração automática dos módulos filhos de parede ao abrir o arquivo.
- Detalhe completo em: `_reversa_forward/004-editor-armario-grudar/data-delta.md`

## 7. Delta de contratos externos

Nenhum. O JSON de produção e o arquivo de módulo salvo da 003 não mudam; `btm_stick` vai junto com o objeto no
`.blend` do módulo salvo e é ignorado se o hospedeiro não for salvo junto.

## 8. Plano de migração

1. Ao abrir um arquivo, `stick.migrate.run` grava `btm_stick` nos módulos filhos de parede (D-08); idempotente,
   marcada por `btm_settings.stick_migrated`.
2. Arquivos salvos com a 004 e abertos numa versão anterior do plugin: `btm_stick` é ignorado e o módulo continua filho
   da parede como antes (sem perda).
3. Nenhum outro dado é apagado ou convertido.

## 9. Riscos e mitigações

| Risco | Impacto | Probabilidade | Mitigação |
|-------|---------|---------------|-----------|
| Undo do editor com edições ao vivo cria passos extras ou perde o passo único | alto | médio | D-22: botões sem `UNDO`, chamadas diretas; fumaça com Ctrl+Z depois do Confirmar e depois do Cancelar |
| Cancelar não volta exatamente o módulo em alguma biblioteca | alto | médio | Fumaça por biblioteca comparando a elevação (D-23) antes de abrir e depois de cancelar; diferença vira bug da biblioteca, não do editor |
| Handler de grudar caro ou em laço em cena grande | médio | médio | Índice hospedeiro → itens montado só quando `btm_stick` muda; trabalha só nos objetos atualizados no depsgraph; meta medida na fumaça |
| Varredura de colisão lenta (200 módulos) | médio | médio | Pré-filtro por caixa orientada antes do BVH, cache de BVH invalidado pelo depsgraph, verificação do item só com vizinhos |
| Falsa colisão em vãos de porta/janela, frentes e peças de canto | médio | alto | BVH da malha avaliada (com furos) confirma o par; RN-12 exclui abertura × parede e peças do mesmo módulo; contato até 1 mm não conta |
| Migração marca o lado errado em produto com recuo (face frame `recess`) | médio | baixo | `distance` negativa = recuo atual; o item não se move na migração, só ganha o vínculo |
| Escopo grande (27 RF em três blocos) | alto | alto | Incrementos I1 → I2 → I3 com fumaça própria; I3 pode ser adiado sem afetar I1 e I2 |

## 10. Critério de pronto

- [ ] Todas as ações do `actions.md` marcadas `[X]`
- [ ] Testes `unittest` dos núcleos puros (`stick/frame.py`, `collision/rules.py`, `cabinet_editor/elevation.py`,
      `cabinet_editor/validate.py`, `History` genérico) passando; teste de fumaça por incremento no Blender 5.2
- [ ] `ruff check caffmob_draw/`, `python3 docs/rag/tools/check_api.py` e `tests/test_i18n_coverage.py` sem erro
- [ ] `cross-check.md` (se executado) sem CRITICAL nem HIGH
- [ ] `regression-watch.md` gerado
- [ ] Re-extração reversa executada e sem regressão vermelha (recomendado, não obrigatório)

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-10-07 | Versão inicial gerada por `/reversa-plan` | reversa |
