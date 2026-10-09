# Roadmap: Editor de armário no modelo do "Construtor de Armários" (Promob)

> Identificador: `008-editor-armario-construtor`
> Data: `2026-10-08`
> Requirements: `_reversa_forward/008-editor-armario-construtor/requirements.md`
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA

## 1. Resumo da abordagem

Delta sobre o editor da 006 (`caffmob_draw/cabinet_editor/`). Todas as abas seguem o mesmo padrão:
- um **catálogo puro** de itens: id, rótulo, descrição, miniatura, parâmetros e restrições de medida;
- um botão **Inserir** que manda um pedido ao modal (o mesmo esquema de rascunho e desfazer da 004/006);
- uma **ponte por tipo de item**, que cria ou atualiza objetos filhos da raiz do módulo, como as divisões da 006.

A entrega é em incrementos que funcionam sozinhos, como pedido no requirements (§10):

| Incremento | Conteúdo | Funciona sozinho? |
|---|---|---|
| **I1 Núcleos puros** | Catálogo, vãos do armário, peças extras, deslizantes, painel de eletro, cotas de posição, estado Aplicar | Testes `unittest` |
| **I2 Fluxo** | 7 abas, barra "Selecionado", OK/Cancelar/**Aplicar**, painel de propriedades, árvore com caixas, vão alvo → vão da biblioteca | Sim: o editor da 006 com o fluxo novo |
| **I3 Abas reaproveitadas** | Divisões (múltipla, catálogo de recuo, móveis, distanciadores, sem divisória), Gavetas (com gavetões, internas, Blum e puxador) e Portas (003, com invertido e linhas de abertura), Fundos (inteiro/recuado, automático) | Sim |
| **I4 Internos** | Painel p/ eletro com recorte, eletros de referência, apoios, pistões, biblioteca | Sim |
| **I5 Deslizantes** | Trilhos (grupo FRAME da 007) + folhas (LEAF da 007) com batentes | Sim |
| **I6 Estrutura completa** | Componentes extras, Número de vãos, Posição e Movimentação | Sim |
| **I6b Ferragens** | Lista de ferragens (pés, pistões, corrediças, trilhos) no painel de produção e no JSON 2.2.0; furação das divisórias móveis em `drilling` | Sim |
| **I7 Acabamento** | Miniaturas, traduções, fumaça, guia | — |

Antes dos painéis (I2), o `/impeccable` faz a passada de desenho das 7 abas em `UILayout`, como na 006.

## 2. Princípios aplicados

`.reversa/principles.md` não existe. Valem o `CLAUDE.md` e o `PRODUCT.md`:

| Princípio | Como a feature se relaciona | Status |
|---|---|---|
| RAG 5.2 | `prop_tabs_enum`, `template_icon_view`/`bpy.utils.previews`, `bpy.ops.ed.undo_push` (Aplicar). Assinaturas confirmadas na codificação | respeita |
| `UNDO` e handlers com remoção | Aplicar = `ed.undo_push` dentro do modal (D-04); nenhum handler novo além do desenho da barra, no `window.py` existente | respeita |
| Textos pt-BR + en-US | RF-14 | respeita |
| PRODUCT 2: convenções do Blender | Abas, grade de botões com ícone e prévias nativas; nenhum widget próprio | respeita |
| PRODUCT 3: cada função num lugar | Frentes e Puxadores saem do Acabamento e vão para Portas e Gavetas; Materiais fica na Estrutura (D-03) | respeita |
| PRODUCT 5: do projeto à produção | Peças novas entram no plano de corte com componente do Configurador; ferragens (pés, pistões, corrediças, trilhos) entram na **lista de ferragens** nova e no JSON (D-24, clarify sessão 2) | respeita |
| CTO Guardian: incremental | Escopo grande por decisão do titular; mitigado pelos incrementos independentes de §1 | respeita |

## 3. Decisões técnicas

| ID | Decisão | Justificativa | Alternativas descartadas | Confidência |
|----|---------|----------------|--------------------------|-------------|
| D-01 | **Catálogo puro** (`cabinet_editor/catalog.py`): itens por aba e subaba com `id`, rótulo, descrição, chave de miniatura, parâmetros (mm), restrição de medida mínima, se aceita "invertido" e a **ação** (tipo de pedido ao modal). Os valores das capturas são o padrão | Elicitação, princípio 1 ("o catálogo não deve conter regra geométrica espalhada na UI"); testável fora do Blender | Itens soltos nos painéis | 🟢 |
| D-02 | Abas: `tab` vai de 3 para **7** valores (`STRUCTURE`, `DIVISIONS`, `DRAWERS`, `INTERIOR`, `DOORS`, `SLIDING`, `BACKS`). Se a barra estiver estreita, a fileira de abas usa só ícone (`icon_only`), com o nome no tooltip; decisão final no `/impeccable` | RN-01; 7 rótulos não cabem lado a lado numa barra de 300 px | Duas fileiras de abas | 🟡 |
| D-03 | A aba Acabamento da 006 deixa de existir. **Frentes**/estilo vão para Portas e Gavetas, **Puxadores** para Portas **e Gavetas** (cada aba aplica às frentes que insere; RN-12), **Materiais** para a Estrutura (grupo recolhido) e **Divisões internas** (quantidade, da 003) para Divisões como "Interior da biblioteca". A lista de componentes da 004 vira a árvore da Estrutura | RF-01 (funções alcançáveis) e PRODUCT 3 | Manter uma 8ª aba | 🟢 |
| D-04 | **Aplicar**: o modal executa `bpy.ops.ed.undo_push(message="Editor de armário: Aplicar")`; depois `draft.initial = draft.current`, e a referência do Cancelar e o "sujo" passam a ser o estado aplicado. OK = Aplicar + fechar. Aplicar fica desabilitado quando não há mudança ou há erro | RN-04 (Q3). O modal da 004 já tem `UNDO`, então o passo do fim do modal continua existindo | Fechar e reabrir o modal (perde a vista e a seleção) | 🟡 |
| D-05 | **Vão alvo**: o subvão da 006 (`session.space`) é o alvo de Divisões, Internos e Fundos. Para Gavetas e Portas, o alvo vira o **vão da biblioteca** que contém o centro do subvão (caixa de cada `adapter.openings` no referencial da vista). A vista destaca esse vão e avisa "A frente ocupa o vão inteiro da biblioteca" quando ele é maior que o subvão | RN-11 (Q2c) | Frentes por subvão (feature seguinte) | 🟢 |
| D-06 | **Barra de estado**: texto no `POST_PIXEL` da vista (`window.py`): "Selecionado: (nenhum) / Vão <rótulo> / <peça>". A seleção de peça e a de vão passam a coexistir: clicar em área livre escolhe vão e clicar em peça escolhe peça, em qualquer aba | RN-03 | Mudar o que o clique faz conforme a aba (006) | 🟢 |
| D-07 | **Árvore da Estrutura**: linhas de `BoolProperty` virtual (get/set) por item. O `set` manda `REMOVE_PART`/`RESTORE_PART` (006) ou `TOGGLE_EXTRA`. Grupos com nós recolhíveis (`panel_prop`) e valor ao lado (`FloatProperty` virtual). Espessura no rótulo | RN-07, RN-07a; captura | `UIList` (sem hierarquia) | 🟡 |
| D-08 | **Gavetas e Portas** reaproveitam `bridge.edit` 'FRONT'/'STYLE'/'PULL' (003/006) no vão da biblioteca (D-05). Mapeamento de Portas: Inteira = 1 porta (lado do invertido); Ambas = `DOUBLE_DOORS`; Esquerda/Direita = `DOOR_LEFT`/`DOOR_RIGHT`; Basculante = `FLIP_UP`; invertido troca Esquerda ↔ Direita. Inferior/Superior/Alta filtram os estilos pela altura do vão (< 900, 900–1500, > 1500 mm) | RN-12, RN-13 | — | 🟡 |
| D-09 | **Linhas de abertura** na vista (`window.py`): para cada frente de porta, traço tracejado do canto da dobradiça ao meio do lado oposto (a convenção do Promob na captura); basculante: do topo ao meio da base | RF-11; captura | — | 🟢 |
| D-10 | **Inserção múltipla** (puro, `divisions.add_many`): N chapas no vão alvo com subvãos iguais, `(tamanho − N·t)/(N+1)`. **Catálogo de recuo**: "Interna s/ Recuo" e "Interna c/ Recuo" preenchem as opções de recuo da 006 | RN-09, RN-10 | — | 🟢 |
| D-11 | **Fundos**: "Inteiro" = fundo da biblioteca (estrutura BACK presente). "Inteiro Recuado" = `btm_structure` BACK ganha `setback` (padrão 0,02 m): o adaptador desloca a peça do fundo para dentro (`btm`: no `layout`; outras bibliotecas: localização da peça reafirmada em `after_rebuild`, como a espessura da 006) e o `inner_spaces` é recortado pela peça nova (o `clip_space` da 006 já faz isso). "Inserir automaticamente" (`auto_back`, padrão ligado): com ele, uma mudança estrutural restaura o fundo removido e reaplica o recuo; desligado, o fundo só muda por ação do projetista | RN-14, RN-15 | Criar um fundo nosso separado do da biblioteca (duplicaria peça) | 🟡 |
| D-12 | **Peças extras e painéis** são `CabinetPart` filhos da raiz com `btm_extra` (tipo, parâmetros) e `btm_component` (Configurador): Base Superior Recuada → `BAS`; Rodapés → `ROD`; Rodapé Granito → `ROD` com material da chapa "Granito"; Fechamentos → `TAMPON`; Vistas e Vistas altas → `ESP`; Painel p/ eletro → `FRE_FORNO`; Apoio → `PRAT` (divisão horizontal da 006); folhas deslizantes → `POR`. Entram no plano de corte pelo caminho da 006 | RN-07a, RN-13a, RN-13b, PRODUCT 5 | Peças sem componente (ficariam UNCLASSIFIED) | 🟡 |
| D-13 | **Geometria das peças extras** (puro, `extras.py`), a partir da caixa da carcaça e das espessuras: rodapé frontal na base da frente, com altura = pés e recuo de 50 mm; rodapés laterais nas faces laterais; fechamento = chapa vertical de largura 50 encostada em cada lateral, por fora; vista = chapa de largura 150 na frente, encostada na lateral do lado; vista alta = vista até o pé-direito (altura da parede ou 2,70 m); Base Superior Recuada = tampo recuado 20 mm na frente; pés = cilindros de 150 nas posições 01 a 04 (cantos da base, com 50 mm de afastamento) | RN-07a. Valores das capturas; posições inferidas | — | 🟡 |
| D-14 | **Pés plásticos** são ferragem: objetos marcados com `btm_hardware='PE_PLASTICO'`, fora do plano de corte de chapas, contados na lista de ferragens (D-24) | RN-07a, RN-16 | Contar como peça de chapa | 🟢 |
| D-15 | **Número de vãos** (puro, `bays.py`): N vãos = N−1 divisórias verticais de vão inteiro no espaço-raiz `s0`, marcadas `bay=True` (divisões da 006), em posições iguais. Mudar N refaz só as marcadas e avisa nos Ajustes automáticos | RN-07b | Mexer nos bays nativos de cada biblioteca (quatro implementações) | 🟡 |
| D-16 | **Posição/Movimentação**: para a divisão selecionada, as cotas saem do subvão (anterior/posterior = recuos; inferior/superior ou esquerda/direita = distâncias às faces). Editar a cota manda `EDIT_DIVISION`. O modal trata ←/→/↑/↓ movendo a divisão selecionada pelo **Passo** (o primeiro toque usa o **Passo inicial** quando ele é > 0) | RN-07c | — | 🟡 |
| D-17 | **Internos** (puro, `appliances.py` + ponte): o painel p/ eletro é uma chapa na frente do vão alvo (largura e altura do vão) com recorte `CPM_CUTOUT` do tamanho do eletro, centrado (reaproveita `aggregates/perforate`). O eletro de referência é uma caixa com material, fora do corte. Medidas de catálogo: forno 595×595×560, micro 595×390×400, cafeteira 595×455×400 (L×A×P, mm). Externo = painel no plano da frente; embutido = painel recuado pela espessura da frente. Apoio = prateleira (divisão horizontal) logo abaixo do eletro. Pistão = ferragem (como D-14). Biblioteca = os módulos salvos da 003 filtrados por categoria "Internos" | RN-13a | Modelar eletros detalhados | 🟡 |
| D-18 | **Deslizantes**: reaproveitam a 007. Um grupo FRAME "Trilhos" (trilho superior + inferior, perfis de 18 mm de profundidade por folha, batentes nas laterais) é filho da raiz, e N folhas (2 ou 3) são `CabinetPart` em grupos LEAF de correr, cada uma num trilho (profundidade escalonada) e com sobreposição de 30 mm. Abrir para na lateral e fechar para no montante da outra (batentes da 007). A largura da folha é `(largura + (N−1)·30)/N`. O estilo fica gravado; nesta feature a geometria é lisa para todos, e os estilos com gola, cava, perfil ou puxador integrado ganham um rasgo vertical simples. Vão sem profundidade para `N × 18 mm` bloqueia | RN-13b; 007 RN-08/RN-09 | Modelar os 18 estilos (fora de proporção) | 🟡 |
| D-19 | **Miniaturas**: PNG gerados por `tools/render_cabinet_thumbnails.py` (Workbench, como `catalog/render_thumbnails.py`), versionados em `caffmob_draw/cabinet_editor/thumbnails/` e carregados com `bpy.utils.previews` (padrão de `standards/previews.py`). Os estilos de porta da biblioteca, que são do projeto, usam um ícone genérico com o nome | NFR usabilidade; precedente no código | Desenhar ícones à mão | 🟡 |
| D-20 | Rascunho: `EditorState` ganha `extras`, `slides`, `interiors`, `backs` (dicionários lidos da cena). `apply_state` reaplica cada um pela ponte do tipo, como `structure`/`divisions` na 006 | RN-04, Cancelar exato | — | 🟢 |
| D-21 | **Inserir sem vão alvo**: o `poll` de `cabinet_editor_insert` testa `session.space` (e o vão da biblioteca para Gavetas e Portas) e desabilita com `poll_message_set("Selecione um vão na vista")`; o painel mostra o mesmo texto ao lado do botão. Não há inserção implícita | RN-05 (clarify sessão 2, Q2; auditoria A001) | Inserir no vão inteiro quando houver um só | 🟢 |
| D-22 | Itens de Divisões (puro em `divisions.py`/`catalog.py`): **Móvel** = divisória com `kind='MOVABLE'`, mesma geometria da fixa, e furação gerada nas duas peças vizinhas (furos de 5 mm a cada 32 mm, a 37 mm da frente e de trás, na faixa da altura do subvão) que sai em `drilling` (D-24). **Distanciador 15/30** = `kind='SPACER'`, chapa de vão inteiro que ocupa a faixa sem criar dois subvãos: o subvão é recortado pela faixa (o `resolve` gera uma folha só). **p/ Divisão** = `kind='SPACER'` com `follow=<uid>` da divisória vizinha, colado a ela e reposicionado junto. **Sem Divisória** = remove a divisória (e as de dentro, regra da 006) do vão alvo | RN-10a (sessão 2, Q1; A002) | Fazer o distanciador como divisória comum (criaria um subvão estreito inútil) | 🟡 |
| D-23 | Subabas de Gavetas: **Gavetas** = `set_front('DRAWERS', n)` (003). **Gavetões** = idem com n de 2 a 4 e o estilo de frente "alto", quando a biblioteca tiver. **Internas** = gavetas por trás de uma porta: no frameless, o interior `InteriorSplitterVertical` com gavetas internas (`ROLLOUT`) que a 003 já usa (`set_interior(drawers=n)`) e porta no vão; nas outras bibliotecas, desabilitado com o motivo. **Blum** = Gavetas com corrediça marcada `BLUM` na lista de ferragens e medidas de catálogo, sem geometria própria. Puxador: o escolhido na aba vai para as frentes de gaveta inseridas (`PULL` da 003) | RN-12 (sessão 2, Q1 e Q4) | Geometria de corrediça Blum (fora de escopo) | 🟡 |
| D-24 | **Lista de ferragens** (`cutting/hardware.py`, puro + coletor): percorre os módulos e soma, por código, os objetos `btm_hardware` (pés, pistões, trilhos) e as frentes de gaveta (2 corrediças por gaveta: `CORREDICA` ou `CORREDICA_BLUM`). Aparece numa caixa "Ferragens" no painel de produção (Produção/Projeto › Plano de corte, 005) e sai no JSON 2.2.0 como `hardware[]`; a furação das divisórias móveis sai em `parts[].drilling` (contrato em `interfaces/cut-plan-json.md`) | RN-16, RN-10a (sessão 2, Q3) | Lista só na tela, sem exportação | 🟢 |
| D-25 | **Tipo do armário** (RN-08): `frameless`/`face frame` pelo `CABINET_TYPE` (BASE → Balcão, UPPER → Aéreo, TALL → Alto, CORNER → Canto); `closets` pelo `closet_type`; `btm` pelo `cabinet_type` (rótulos do enum); sem tipo, o nome da biblioteca (`classify.LIBRARY_LABELS`) | RN-08 (auditoria A006) | — | 🟢 |

## 4. Premissas

| Premissa | Origem (`requirements.md` seção) | Risco se errada |
|----------|----------------------------------|-----------------|
| Geometria das peças extras conforme D-13 | §10 (RN-07a) | Médio: ajustar `extras.py` (puro, testado) |
| Medidas de catálogo dos eletros conforme D-17 | §10 (RN-13a) | Baixo: são parâmetros do catálogo |
| Deslizantes: perfil de 18 mm por folha, sobreposição de 30 mm, geometria lisa por estilo | §10 (RN-13b) | Médio: visual simplificado dos estilos |
| Furação das móveis: 5 mm, passo 32, a 37 mm de frente e trás | D-22 | Baixo: parâmetros do catálogo |
| Corrediça = 2 por gaveta (um par) | D-24 | Baixo: regra do coletor |
| Aplicar por `ed.undo_push` dentro do modal | D-04 | Médio: se o Blender recusar o push no modal, Aplicar passa a fechar e reabrir o editor |

## 5. Delta arquitetural

| Componente | Arquivo de origem no legado | Tipo de mudança | Resumo |
|------------|------------------------------|-----------------|--------|
| Núcleos puros | `cabinet_editor/catalog.py`, `extras.py`, `bays.py`, `slides.py`, `appliances.py`, `position.py`; `divisions.py` (add_many) | componente-novo / regra-alterada | Regras geométricas e catálogo testáveis |
| Estado e rascunho | `cabinet_editor/state.py`, `props.py`, `ops_editor.py` | regra-alterada | 7 abas, Aplicar, setas, vão da biblioteca, seleção dupla |
| Ponte com a cena | `cabinet_editor/bridge.py`, `scene_extras.py`, `scene_slides.py`, `scene_interiors.py` | regra-alterada / componente-novo | Criar, atualizar e apagar as peças novas |
| Adaptadores | `customize/adapters/*.py`, `common.py` | regra-alterada | Recuo do fundo (`set_back_setback`) e caixas dos vãos da biblioteca (`opening_boxes`) |
| Painéis | `cabinet_editor/panels*.py` (+ `panels_drawers.py`, `panels_interior.py`, `panels_doors.py`, `panels_sliding.py`, `panels_backs.py`) | regra-alterada / componente-novo | Uma aba por arquivo |
| Vista | `cabinet_editor/window.py` | regra-alterada | Barra de estado, linhas de abertura, vão da biblioteca destacado |
| Miniaturas | `tools/render_cabinet_thumbnails.py`, `cabinet_editor/thumbnails/`, `cabinet_editor/previews.py` | componente-novo | PNG versionados + prévias |
| Plano de corte | `cutting/part_sources.py` | regra-alterada | Ferragem (`btm_hardware`) fora; peças `btm_extra` com componente; deslizantes e painéis no `btm` sintético |
| Ferragens | `cutting/hardware.py` (novo), `cutting/json_exporter.py`, painel do plano de corte (`ui/sidebar_project.py`) | componente-novo / contrato-alterado | Lista de ferragens; JSON 2.2.0 com `hardware[]` e `drilling` preenchido |
| Reaplicar | `customize/reapply.py` | regra-alterada | `after_rebuild` reafirma recuo do fundo e reposiciona extras/deslizantes/internos |
| Traduções | `data/translations/cabinet_editor.json` | regra-alterada | Textos novos |

## 6. Delta no modelo de dados

- Resumo das mudanças:
  - `Object.btm_extra` (peças extras, painéis, eletros, trilhos e folhas);
  - `btm_structure` ganha `back_setback`, `auto_back` e os extras marcados;
  - `btm_division` ganha `bay` (vão gerado pelo Número de vãos);
  - `WindowManager.btm_cabinet_editor` ganha as 7 abas, as opções de cada aba e passo/passo inicial;
  - `EditorState` ganha `extras`, `slides`, `interiors` e `backs`.
- Detalhe completo em: `_reversa_forward/008-editor-armario-construtor/data-delta.md`

## 7. Delta de contratos externos

| Contrato | Tipo | Arquivo de detalhe |
|----------|------|--------------------|
| JSON de produção (`caffmob_draw.project`) 2.1.0 → **2.2.0** | arquivo | `_reversa_forward/008-editor-armario-construtor/interfaces/cut-plan-json.md` |

O manifesto do módulo salvo (1.1.0, 006) não muda: as peças novas viajam no `.blend`.

## 8. Plano de migração

1. Editores abertos antes da atualização: a aba `FINISH` (006) não existe mais e cai em `STRUCTURE`.
2. Módulos sem `btm_extra` nem recuo de fundo continuam iguais.
3. Divisões da 006 sem `bay` são divisões comuns: o Número de vãos não as toca.

## 9. Riscos e mitigações

| Risco | Impacto | Probabilidade | Mitigação |
|-------|---------|---------------|-----------|
| Escopo grande (7 abas, 4 motores novos) | alto | alto | Incrementos independentes (§1); cada um com fumaça própria e commit possível |
| `ed.undo_push` dentro do modal (Aplicar) | médio | médio | Testar no I2 antes de seguir; alternativa em §4 |
| Recuo do fundo desfeito pelo recálculo das bibliotecas | médio | médio | Reafirmar em `after_rebuild`, como a espessura da 006 |
| Estilos de deslizante só com geometria simplificada | médio | alto | Registrado como premissa; o estilo fica gravado para ganhar a geometria certa depois |
| Barra lateral apertada com 7 abas | baixo | alto | Abas só com ícone + tooltip (D-02); passada do `/impeccable` |
| Miniaturas geradas fora do Blender do usuário | baixo | baixo | PNG versionados; sem miniatura, aparece um ícone nativo |
| Leitores do JSON 2.1 quebrarem com `hardware[]` | médio | baixo | Campo novo opcional, major mantido (2.x); `validate` aceita 2.0–2.2 |

## 10. Critério de pronto

- [ ] Todas as ações do `actions.md` marcadas `[X]`
- [ ] `cross-check.md` (se executado) sem CRITICAL nem HIGH
- [ ] `regression-watch.md` gerado
- [ ] `unittest` dos núcleos novos; `ruff`, `check_api.py` e `test_i18n_coverage` sem erro
- [ ] Fumaça com janela nas quatro bibliotecas, uma seção por incremento, incluindo Aplicar/Cancelar e um passo de
      desfazer por Aplicar
- [ ] Caso de referência do Promob reproduzido num `btm` de 800 × 2250 × 550 com laterais de 15: largura interna 770
- [ ] Fumaças da 003, 004, 006 e 007 sem regressão

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-10-08 | Versão inicial gerada por `/reversa-plan` | reversa |
| 2026-10-08 | Atualização após a auditoria e a sessão 2 do clarify: D-21 a D-25, D-03 e D-14 revistos, I6b, contrato JSON 2.2.0 | reversa |
