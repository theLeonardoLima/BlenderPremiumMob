# Requirements: Editor de armário no modelo do "Construtor de Armários" (Promob)

> Identificador: `008-editor-armario-construtor`
> Data: `2026-10-08`
> Pasta da extração reversa: `_reversa_sdd/`
> Origem: pedido do titular ("usando o /impeccable, leia toda a documentação em anexo e implemente melhorias no
> editor de armário"). Anexos em `inputs/`:
> - `elicitacao-construtor-de-armarios-v2.md`: 36 RF, 18 RN e 24 CA da elicitação, com 15 lacunas;
> - 20 capturas do Promob Plus 5.60.46.6, das quais 10 nomeadas por aba (TELA INICIAL, DIVISOES, GAVETAS, INTERNOS,
>   PORTAS, DESLIZANTES, FUNDO).
>
> Nota de evidência: o vídeo citado na elicitação não está no anexo. As capturas foram lidas diretamente e confirmam
> as abas, os rótulos e os estados descritos.
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA / DÚVIDA

## 1. Resumo executivo

O editor de armário da 006 tem três abas: Estrutura, Divisão e Acabamento. O projetista acostumado ao Promob espera o
fluxo do **Construtor de Armários**:
- uma aba por tipo de coisa que entra no móvel (Estrutura, Divisões, Gavetas, Internos, Portas, Deslizantes e Fundos);
- o **vão selecionado** na vista como alvo de tudo o que se insere;
- a barra "Selecionado: …";
- um catálogo com miniaturas e **Inserir**;
- **OK / Cancelar / Aplicar**.

Esta feature leva o editor a esse modelo **completo**, com as 7 abas e os catálogos confirmados nas capturas
(decisão do titular, clarify Q1). A entrega é em incrementos dentro da feature:
1. o fluxo (abas, vão alvo, barra, OK/Cancelar/Aplicar);
2. as abas que reaproveitam o plugin (Estrutura, Divisões, Gavetas, Portas, Fundos);
3. as abas novas (Internos, Deslizantes) e os componentes extras da Estrutura.

Gavetas e portas entram no vão da biblioteca agora e no subvão da 006 numa feature seguinte (Q2).

## 2. Contexto a partir do legado

| Fonte | Trecho relevante | Confidência |
|-------|------------------|-------------|
| `_reversa_sdd/domain.md#1.1 Entidades do Ambiente 3D` | Módulo = armário paramétrico de painéis MDF/MDP | 🟢 |
| `_reversa_sdd/domain.md#1.2 Entidades de Produção` | Toda peça entra no plano de corte | 🟢 |
| `_reversa_forward/006-editor-armario-abas/requirements.md#4` (RN-01 a RN-16) | Editor em abas (Estrutura, Divisão, Acabamento); componentes externos com remover/restaurar e 3 modos; divisões por subvão com recuos; rascunho com Confirmar/Cancelar e um passo de desfazer | 🟢 |
| `_reversa_forward/004-editor-armario-grudar/requirements.md#4` (RN-01 a RN-04) | Editor numa janela própria com vista frontal, rascunho, mensagens com gravidade e ajustes automáticos | 🟢 |
| `_reversa_forward/003-modulos-agregados-reposicionar/requirements.md#5` (RF-01 a RF-10) | Frentes por vão da biblioteca: porta esquerda/direita, duas portas, gavetas (1 a 8), basculante, painel, vazio; estilos de porta e gaveta; puxadores | 🟢 |
| `caffmob_draw/cabinet_editor/panels.py`, `panels_structure.py`, `panels_divisions.py` | Abas atuais e rodapé fixo; Frentes/Puxadores/Materiais/Divisões internas na aba Acabamento | 🟢 |
| `caffmob_draw/cabinet_editor/window.py` | Vista frontal com subvão destacado e chapas removidas tracejadas | 🟢 |
| `inputs/elicitacao-construtor-de-armarios-v2.md#2` | Abas, tipo "Torre p/ Eletros", medidas 800/2250/550/770/340/1880, árvore de componentes com checkboxes, Posição, Movimentação, OK/Cancelar/Aplicar | 🟢 |
| `inputs/GAVETAS EDITOR DE ARMÁRIO LEGADO -- 001.png` | Vão em vermelho com cotas 340/1880; Opções de gavetas (Gaveta c/ CF), Opções de frentes (Reta), Número de gavetas 4, Inserir; painel "Não há propriedades disponíveis!"; "Selecionado: Vão" | 🟢 |
| `inputs/PORTAS EDITOR DE ARMÁRIO LEGADO -- 001.png` | Filtros Inferior/Superior/Alta/Basculante e Ambas/Inteira/Esquerda/Direita; 12+ estilos com miniatura; Inserir invertido; linhas de abertura tracejadas | 🟢 |
| `inputs/FUNDO EDITOR DE ARMÁRIO LEGADO -- 001.png` | Inteiro / Inteiro Recuado; "Inserir automaticamente" marcado; Fundo Inteiro 15mm | 🟢 |
| `inputs/elicitacao-construtor-de-armarios-v2.md#13` | 15 lacunas, entre elas: efeito de Aplicar, cotas de Posição, Movimentação, distribuição de gavetas, regras de deslizantes e basculantes | 🔴 |

## 3. Personas e cenários de uso

| Persona | Objetivo | Cenário-chave |
|---------|----------|---------------|
| Projetista vindo do Promob | Montar o armário no fluxo que já conhece | Abre o editor, clica no vão de cima (a vista o destaca e a barra diz "Selecionado: Vão 1 › de cima"), vai em Gavetas, escolhe 4 e clica Inserir |
| Projetista de interiores | Testar variações sem fechar o editor | Insere portas, clica **Aplicar**, confere no 3D, troca o estilo e clica **OK** |
| Marceneiro (produção) | Fundo correto | Na aba Fundos escolhe "Inteiro Recuado" e o plano de corte sai com o fundo recuado |

## 4. Regras de negócio novas ou alteradas

**Glossário desta feature.**
- *Vão alvo*: o subvão escolhido na vista (006) ou o vão da biblioteca que o contém (003), sobre o qual as abas
  inserem.
- *Catálogo*: as opções de uma aba (tipo de gaveta, estilo de porta, tipo de fundo), cada uma com nome, miniatura e
  descrição.
- *Aplicar*: grava o estado atual como ponto de confirmação sem fechar o editor.

**A. Fluxo e janela**

1. **RN-01:** As abas do editor passam a seguir os nomes e a ordem do Construtor de Armários: **Estrutura, Divisões,
   Gavetas, Internos, Portas, Deslizantes, Fundos**. As funções da aba Acabamento da 006 (puxadores, materiais)
   continuam acessíveis. 🟢 (captura; clarify Q1)
   - Origem no legado: `_reversa_forward/006-editor-armario-abas/requirements.md#4` (RN-01)
   - Tipo: alterada
2. **RN-02:** Escopo: as **7 abas completas**, com os catálogos confirmados nas capturas, incluindo Internos
   (eletros), Deslizantes e os componentes extras da Estrutura. Ficam de fora só a barra de ferramentas do Construtor
   (zoom, pan e régua já existem no Blender e na vista) e o motor de frentes por subvão (feature seguinte, Q2). 🟢
   (clarify 2026-10-08, Q1)
   - Tipo: nova
3. **RN-03:** A barra de estado da vista mostra o que está selecionado: "Selecionado: (nenhum)", "Selecionado: Vão
   <nome>" ou "Selecionado: <componente>". 🟢 (captura)
   - Tipo: nova
4. **RN-04:** **Aplicar** grava as mudanças como um passo de desfazer e mantém o editor aberto; o novo ponto vira a
   referência de Cancelar. **OK** aplica e fecha. **Cancelar** volta ao último Aplicar (ou à abertura). Aplicar fica
   desabilitado sem mudança pendente e com erro bloqueante. 🟢 (clarify 2026-10-08, Q3)
   - Origem no legado: `_reversa_forward/004-editor-armario-grudar/requirements.md#4` (RN-01)
   - Tipo: alterada
5. **RN-05:** Toda aba de inserção (Divisões, Gavetas, Internos, Portas, Deslizantes, Fundos) opera sobre o **vão
   alvo**. Sem vão alvo, **Inserir fica desabilitado** com "Selecione um vão na vista". Não há inserção implícita no
   vão inteiro. 🟢 (elicitação RN-006; clarify 2026-10-08 sessão 2, Q2)
   - Tipo: nova
6. **RN-06:** Quando o item da aba não tem propriedades editáveis, o painel de propriedades mostra "Não há propriedades
   disponíveis" em vez de campos vazios. 🟢 (captura)
   - Tipo: nova

**B. Estrutura**

7. **RN-07:** Os componentes externos da 006 aparecem como **árvore com caixa de marcar**: marcada = presente;
   desmarcar = remover (modo padrão Manter tudo da 006); marcar de novo = restaurar. A espessura aparece no nome
   ("Lateral Esquerda 15mm"). 🟢 (captura; mecanismo da 006)
   - Origem no legado: `_reversa_forward/006-editor-armario-abas/requirements.md#4` (RN-04, RN-06)
   - Tipo: alterada
7a. **RN-07a:** A árvore ganha os **componentes extras** do Construtor, cada um com caixa de marcar e o parâmetro ao
    lado. Os valores padrão são os das capturas. Cada componente marcado vira peça de produção e entra no plano de
    corte; os pés plásticos são ferragem, ficam fora do corte e entram na **lista de ferragens** (RN-16).
    - Base Superior Recuada: tampo recuado na frente pelo recuo padrão da 006, 20 mm;
    - Pés Plásticos: altura 150 e posições 01 a 04, cada posição liga ou desliga um pé num canto;
    - Rodapés Frontal, Esquerdo e Direito: altura = pés;
    - Rodapés Granito: rodapé frontal em material Granito;
    - Fechamentos: chapa lateral de largura 50 nos dois lados;
    - Vistas Frontal, Esquerda e Direita: largura 150;
    - Vistas (alto) Esquerda, Direita e Frontal: vistas que sobem até o teto.

    🟢 (itens e valores: captura); 🟡 (geometria de cada item)
    - Tipo: nova
7b. **RN-07b:** **Número de vãos** (1 a 10) divide o armário em vãos iguais com divisórias verticais de vão inteiro
    (as da 006). Diminuir o número remove as divisórias de vão a mais e avisa nos Ajustes automáticos. 🟢 (campo);
    🟡 (efeito)
    - Tipo: nova
7c. **RN-07c:** **Posição** (modo Livre) mostra, para o componente ou divisão selecionado, as distâncias às faces
    internas: anterior (frente), posterior (trás), inferior e superior. Os campos ficam desabilitados sem seleção, como
    na captura. Editar uma cota move o item. **Movimentação**: **Passo** (padrão 10 mm) é o quanto as setas do teclado
    movem o item selecionado na vista, e **Passo inicial** (padrão 0) é o primeiro deslocamento. 🟢 (campos); 🟡
    (efeito: lacunas 3 e 9 da elicitação)
    - Tipo: nova
8. **RN-08:** A Estrutura mostra o **tipo do armário** e as definições: largura total, altura e profundidade com a
   faixa. O tipo é o nome do tipo na biblioteca: no frameless e no face frame, Balcão/Aéreo/Alto/Canto; no closets, o
   tipo do starter; no `btm`, Balcão Inferior/Aéreo/Paneleiro. Sem tipo conhecido, mostra a biblioteca. 🟢 (captura)
   - Tipo: alterada

**C. Divisões**

9. **RN-09:** A aba Divisões ganha a **inserção múltipla**: N chapas iguais de uma vez no vão alvo, com espaçamento
   igual entre elas, na orientação escolhida. 🟢 (aba "Inserção múltipla" na captura); distribuição igual 🟡
   - Origem no legado: `_reversa_forward/006-editor-armario-abas/requirements.md#4` (RN-09 a RN-14)
   - Tipo: alterada
10. **RN-10:** As opções "com recuo frontal" e "sem recuo frontal" da 006 aparecem como **itens de catálogo**
    (miniatura + nome), além das caixas de recuo. 🟢 (captura)
    - Tipo: alterada

10a. **RN-10a:** Os demais itens da aba Divisões são implementados com este comportamento:
     - **Divisórias Móveis:** prateleira ou divisória **regulável**. A geometria é a da divisória fixa, com marcação
       de furação na peça (aparece na usinagem do plano de corte), sem fixação.
     - **Distanciador 15mm / Duplo 30mm:** chapa estreita de vão inteiro na espessura indicada, que afasta componentes
       vizinhos. Não divide o vão em dois: ocupa a faixa e reduz o subvão.
     - **Distanciador p/ Divisão 15mm:** distanciador que acompanha uma divisória existente, colado a ela; muda junto
       quando ela se move.
     - **Sem Divisória:** remove a divisória do vão alvo e junta os subvãos.

     🟢 (clarify 2026-10-08 sessão 2, Q1)
     - Tipo: nova

**D. Gavetas e Portas**

11. **RN-11:** As abas Gavetas e Portas inserem frentes no **vão da biblioteca** que contém o vão alvo, pelo mecanismo
    da 003: o vão inteiro da biblioteca ganha a frente. A vista destaca esse vão inteiro e o painel avisa quando o vão
    alvo é menor que ele. A inserção no subvão da 006 fica para uma feature seguinte. 🟢 (clarify 2026-10-08, Q2)
    - Origem no legado: `_reversa_forward/003-modulos-agregados-reposicionar/requirements.md#5` (RF-01 a RF-04)
    - Tipo: alterada
12. **RN-12:** Gavetas: o projetista escolhe a quantidade (1 a 8, padrão 4), o estilo de frente e o **puxador** e clica
    Inserir; as gavetas dividem a altura do vão em partes iguais. Subabas com este comportamento:
    - **Gavetas:** o descrito acima;
    - **Gavetões:** gavetas de frente alta, 2 a 4 por vão;
    - **Internas:** gaveta atrás de porta, com frente recuada pela espessura da porta, sem puxador externo;
    - **Blum:** gaveta com corrediça da marca, só com nome e medidas de catálogo.

    🟢 (captura; limite 8 da 003; clarify sessão 2, Q1 e Q4)
    - Tipo: alterada
13. **RN-13:** Portas: filtros de **tipo** (Inteira = uma porta no vão, Ambas = duas portas, Esquerda, Direita,
    Basculante) e **estilo** (os estilos de porta da biblioteca, com miniatura). **Inserir invertido** troca o lado da
    dobradiça (esquerda ↔ direita; basculante: cima ↔ baixo). A vista desenha as linhas de abertura tracejadas. 🟢
    (captura; clarify Q4)
    - Tipo: alterada

**E. Internos e Deslizantes**

13a. **RN-13a:** A aba **Internos** insere no vão alvo os itens confirmados nas capturas, com miniatura:
     - **Painel p/ Eletros**, com os filtros Externos e Embutidos: Painel Forno/Micro Externo, Painel Forno Externo,
       Painel Micro Externo, Painel Cafeteira Externo, Frontal Externo e Respiro;
     - **eletros** de referência: Forno, Microondas e Cafeteira (volumes com medidas de catálogo, fora do corte);
     - **Apoios**: prateleira de apoio de eletro;
     - **Pistões**: ferragem de basculante.

     O painel é chapa de produção: a frente do vão com o recorte do eletro. O eletro é acessório. Um item que não cabe
     no vão aparece desabilitado com a medida mínima. A subaba **Biblioteca** lista os itens salvos pelo usuário
     ("Salvar como módulo" da 003). 🟢 (itens: captura); 🟡 (medidas de catálogo, Apoios e Pistões)
     - Tipo: nova
13b. **RN-13b:** A aba **Deslizantes** insere portas de correr no armário:
     - famílias **Alumínio** e **Madeira**;
     - estilos Lisa, Reta, Almofada, Fresada, Colonial, Bicolor, Gola Vertical, Gola Vertical 2L, Borda Alumínio, Cava
       Vertical, Chanfrada, Country, Perfil Y Vertical e Perfil Y Vertical 2L, e os de puxador integrado (Obispa,
       Contatto, Torralba, Altero);
     - número de folhas (2 ou 3, padrão 2), trilhos em profundidades diferentes e sobreposição entre folhas;
     - folhas que abrem e fecham com os batentes da 007 (param na lateral e no montante da outra folha).

     Inserir invertido troca a folha da frente. Vão sem profundidade para os trilhos fica bloqueado com a medida
     necessária. 🟢 (famílias e estilos: captura); 🟡 (trilhos, folhas e sobreposição)
     - Origem no legado: `_reversa_forward/007-janela-obj-folhas-colisao/requirements.md#4` (RN-08, RN-09)
     - Tipo: nova

**F. Ferragens**

15a. **RN-16:** Passa a existir uma **lista de ferragens** junto do plano de corte, com nome, código, quantidade e
     módulo. Entram nela os pés plásticos, os pistões, as corrediças de gaveta (inclusive Blum) e os trilhos dos
     deslizantes. Ela aparece no painel de produção e sai na exportação de produção (JSON). 🟢 (clarify 2026-10-08
     sessão 2, Q3)
     - Origem no legado: `_reversa_forward/003-modulos-agregados-reposicionar/interfaces/cut-plan-json.md`
     - Tipo: nova

**G. Fundos**

14. **RN-14:** A aba Fundos tem **Inteiro** e **Inteiro Recuado**. "Inteiro Recuado" afasta o fundo para dentro pela
    medida do recuo (padrão **20 mm**, editável), e o vão interno passa a terminar no fundo recuado (as divisões
    acompanham). 🟢 (opções: captura; 20 mm: clarify Q5)
    - Tipo: nova
15. **RN-15:** "Inserir automaticamente" (marcado por padrão) mantém o fundo presente e recalculado depois de mudar
    medidas, divisões ou estrutura. Desmarcado, o fundo só muda pelo projetista. 🟢 (captura); efeito 🟡
    - Tipo: nova

## 5. Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de aceite | Confidência |
|----|-----------|------------|--------------------|-------------|
| RF-01 | As 7 abas na ordem do Construtor (RN-01, RN-02) | Must | Ao abrir o editor aparecem Estrutura, Divisões, Gavetas, Internos, Portas, Deslizantes e Fundos, com Estrutura aberta; puxadores e materiais continuam alcançáveis | 🟢 |
| RF-02 | Barra "Selecionado: …" na vista (RN-03) | Must | Sem nada: "Selecionado: (nenhum)"; clicar num vão: "Selecionado: Vão 1 › de cima"; clicar numa peça: o nome dela | 🟢 |
| RF-03 | OK / Cancelar / Aplicar (RN-04) | Must | Aplicar sem mudança fica desabilitado; depois de inserir gavetas, Aplicar grava e o editor continua aberto; Cancelar volta ao estado aplicado; OK fecha | 🟡 |
| RF-04 | Inserir só com vão alvo (RN-05) | Must | Sem vão, o botão Inserir de Gavetas, Portas e Divisões fica desabilitado com "Selecione um vão na vista" | 🟢 |
| RF-05 | Painel de propriedades com estado vazio (RN-06) | Should | Selecionar um item sem propriedade mostra "Não há propriedades disponíveis" | 🟢 |
| RF-06 | Árvore de componentes com caixa de marcar e espessura no nome (RN-07) | Must | Desmarcar "Lateral Direita 15mm" a remove (Manter tudo); marcar devolve igual | 🟢 |
| RF-07 | Tipo do armário e definições na Estrutura (RN-08) | Should | Um balcão frameless mostra "Tipo: Balcão" e largura/altura/profundidade com faixa | 🟢 |
| RF-07a | Componentes extras na árvore: base superior recuada, pés plásticos (posições 01–04), rodapés frontal/esquerdo/direito, rodapé granito, fechamentos, vistas e vistas altas (RN-07a) | Must | Marcar "Rodapés › Frontal" cria o rodapé frontal na altura dos pés e ele entra no plano de corte; marcar "Pés Plásticos" põe 4 pés de 150 fora do corte | 🟡 |
| RF-07b | Número de vãos (RN-07b) | Must | Balcão de 800 com 1 → 2 vãos: uma divisória vertical no meio; 2 → 1 remove e avisa | 🟡 |
| RF-07c | Posição e Movimentação do item selecionado (RN-07c) | Should | Divisão selecionada: as cotas mostram as distâncias às faces; digitar a cota inferior move a divisão; setas movem pelo passo de 10 mm | 🟡 |
| RF-08 | Inserção múltipla de divisões (RN-09) | Must | Vão de 768 mm, 3 verticais de 15 mm: quatro subvãos iguais de (768 − 45)/4 | 🟡 |
| RF-09 | Catálogo de divisória com e sem recuo frontal, com miniatura (RN-10) | Should | Escolher "Com recuo frontal" e Inserir cria a chapa com o recuo da frente marcado | 🟢 |
| RF-10 | Gavetas: quantidade, estilo de frente e Inserir no vão da biblioteca do vão alvo (RN-11, RN-12) | Must | Com o vão selecionado, 4 gavetas e Inserir: 4 frentes de altura igual no vão da biblioteca, sem sobreposição | 🟢 |
| RF-11 | Portas: tipo, estilo com miniatura, Inserir invertido (lado da dobradiça) e linhas de abertura (RN-11, RN-13) | Must | "Ambas" + "Lisa" + Inserir: duas portas no vão, linhas de abertura tracejadas na vista; "Esquerda" invertida vira "Direita" | 🟢 |
| RF-11a | Aba Internos: painéis p/ eletros (externos/embutidos), eletros de referência, apoios, pistões e biblioteca do usuário (RN-13a) | Must | "Painel Forno Externo" no vão de cima cria o painel com o recorte e o forno de referência; item que não cabe fica desabilitado com a medida mínima | 🟡 |
| RF-11b | Aba Deslizantes: famílias, estilos, folhas, trilhos, sobreposição e abrir/fechar com batentes (RN-13b) | Must | "Madeira › Gola Vertical 2L", 2 folhas: duas portas de correr em trilhos distintos; abrir uma para na lateral e fechar para no montante da outra | 🟡 |
| RF-12 | Fundos Inteiro e Inteiro Recuado (RN-14) | Must | "Inteiro Recuado" afasta o fundo 20 mm; a profundidade do vão e das divisões diminui 20 mm; o plano de corte mostra o fundo | 🟡 |
| RF-09a | Divisórias Móveis, Distanciadores e Sem Divisória (RN-10a) | Must | Distanciador Duplo num vão de 768 reserva 30 mm e o subvão fica com 738; Sem Divisória remove a divisória do vão alvo e junta os subvãos | 🟢 |
| RF-10a | Subabas Gavetões, Internas e Blum, e puxador na aba Gavetas (RN-12) | Must | Gavetas internas saem com frente recuada e sem puxador; Gavetões aceita só 2 a 4; o puxador escolhido vale para as gavetas inseridas | 🟢 |
| RF-16 | Lista de ferragens no painel de produção e na exportação (RN-16) | Must | Com 4 pés e 4 gavetas, a lista mostra "Pé plástico ×4" e "Corrediça ×4" (pares) e o JSON de produção traz a seção de ferragens | 🟢 |
| RF-13 | Inserir automaticamente o fundo (RN-15) | Should | Com a caixa marcada, mudar a largura recalcula o fundo; desmarcada, o fundo não muda | 🟡 |
| RF-14 | Textos novos em pt-BR e en-US | Must | Em inglês, as abas aparecem como Structure, Divisions, Drawers, Interior, Doors, Sliding, Backs | 🟢 |
| RF-15 | Desenho das abas com `/impeccable`, restrito a `UILayout` | Must | Brief de desenho registrado antes dos painéis, como na 006 | 🟢 |

## 6. Requisitos Não Funcionais

| Tipo | Requisito | Evidência ou justificativa | Confidência |
|------|-----------|----------------------------|-------------|
| Desempenho | A vista e o painel atualizam em até 0,5 s depois de Inserir, num armário com até 20 divisões | Mesma meta da 006 | 🟡 |
| Confiabilidade | Cancelar devolve o estado do último Aplicar exatamente; OK e Aplicar geram um passo de desfazer cada | Elicitação RNF-006, RNF-007; 004 RN-01 | 🟢 |
| Confiabilidade | Nenhuma inserção apaga componente existente sem aviso nos Ajustes automáticos | Elicitação RN-018 | 🟢 |
| Usabilidade | Cada aba cabe sem rolagem numa barra de 1080 px com até 12 miniaturas de catálogo | Capturas: catálogo em grade | 🟡 |
| Compatibilidade | Funciona nas quatro bibliotecas onde a capacidade existir; o que a biblioteca não faz aparece desabilitado com o motivo (padrão da 003/006) | 006 RN-07 | 🟢 |
| Acessibilidade | Estado em texto além da cor (vão selecionado, removido, desabilitado) | `PRODUCT.md` | 🟢 |

## 7. Critérios de Aceitação

```gherkin
Cenário: Abas no modelo do Construtor
  Dado um balcão frameless inserido
  Quando o projetista abre o editor de armário
  Então vê as abas Estrutura, Divisões, Gavetas, Internos, Portas, Deslizantes e Fundos, nessa ordem
  E a barra da vista diz "Selecionado: (nenhum)"

Cenário: Selecionar o vão
  Dado o editor aberto com uma divisão horizontal
  Quando o projetista clica no vão de cima na vista
  Então o vão fica destacado
  E a barra diz "Selecionado: Vão 1 › de cima"

Cenário: Inserir sem vão
  Dado o editor aberto sem vão selecionado
  Quando o projetista abre a aba Gavetas
  Então o botão Inserir está desabilitado com "Selecione um vão na vista"

Cenário: Inserir gavetas
  Dado o vão de cima selecionado
  Quando o projetista escolhe 4 gavetas, frente Reta, e clica Inserir
  Então o vão recebe 4 gavetas de altura igual, sem sobreposição

Cenário: Inserir portas com abertura desenhada
  Dado o vão selecionado
  Quando o projetista escolhe "Ambas", estilo "Lisa" e clica Inserir
  Então o vão recebe duas portas
  E a vista mostra as linhas de abertura tracejadas

Cenário: Árvore de componentes
  Dado a aba Estrutura de um balcão com laterais de 15 mm
  Quando o projetista desmarca "Lateral Direita 15mm"
  Então a lateral direita sai do armário
  Quando marca de novo
  Então ela volta igual

Cenário: Inserção múltipla
  Dado um vão de 768 mm selecionado
  Quando o projetista escolhe Inserção múltipla, 3 verticais, e clica Inserir
  Então surgem 3 divisórias e 4 subvãos de largura igual

Cenário: Fundo recuado
  Dado um armário com divisão vertical
  Quando o projetista escolhe "Inteiro Recuado" na aba Fundos
  Então o fundo se afasta 20 mm para dentro
  E a divisão passa a terminar no fundo recuado

Cenário: Aplicar sem fechar
  Dado o editor com gavetas inseridas
  Quando o projetista clica Aplicar
  Então o armário é atualizado, o editor continua aberto e Aplicar fica desabilitado
  Quando ele insere portas e clica Cancelar
  Então o armário volta ao estado do Aplicar, com as gavetas

Cenário: Aplicar com erro
  Dado uma divisão com subvão menor que 50 mm
  Quando o projetista tenta Aplicar ou OK
  Então os dois ficam desabilitados e a mensagem DIV-001 aparece

Cenário: Componentes extras
  Dado a aba Estrutura de um balcão frameless
  Quando o projetista marca "Rodapés › Frontal" e "Pés Plásticos"
  Então o balcão ganha o rodapé frontal na altura dos pés e 4 pés de 150
  E o plano de corte lista o rodapé e não lista os pés

Cenário: Número de vãos
  Dado um armário de 800 com 1 vão
  Quando o projetista muda o Número de vãos para 2
  Então surge uma divisória vertical no meio
  Quando ele volta para 1
  Então a divisória sai e os Ajustes automáticos avisam

Cenário: Painel para eletro
  Dado o vão de cima selecionado, com 340 de altura
  Quando o projetista escolhe "Painel Forno Externo" na aba Internos e clica Inserir
  Então o vão recebe o painel com o recorte do forno e o forno de referência
  E um item maior que o vão aparece desabilitado com a medida mínima

Cenário: Porta deslizante
  Dado um armário de 1600 de largura selecionado
  Quando o projetista escolhe "Madeira › Gola Vertical 2L", 2 folhas, e clica Inserir
  Então surgem duas portas de correr em trilhos diferentes, com sobreposição
  E abrir uma folha a faz parar na lateral, e fechá-la para no montante da outra

Cenário: Porta deslizante sem espaço para trilho
  Dado um vão com profundidade menor que a exigida pelos trilhos
  Quando o projetista abre a aba Deslizantes
  Então Inserir fica desabilitado com a profundidade necessária

Cenário: Distanciador duplo
  Dado um vão de 768 mm selecionado
  Quando o projetista insere "Distanciador Duplo 30mm"
  Então o vão passa a ter 738 mm livres e não é dividido em dois

Cenário: Lista de ferragens
  Dado um armário com Pés Plásticos e 4 gavetas
  Quando o projetista gera o plano de corte
  Então a lista de ferragens mostra os 4 pés e as corrediças das 4 gavetas
  E a exportação de produção traz essas ferragens

Cenário: Item sem propriedades
  Dado a aba Fundos com "Fundo Inteiro" selecionado
  Quando não há propriedade editável
  Então o painel de propriedades mostra "Não há propriedades disponíveis"
```

## 8. Prioridade MoSCoW

| Item | MoSCoW | Justificativa |
|------|--------|---------------|
| RF-01 a RF-04, RF-06 | Must | O fluxo do Construtor (abas, vão alvo, barra, Aplicar, árvore) é o centro do pedido |
| RF-08, RF-10, RF-11, RF-12 | Must | Abas de inserção que reaproveitam 003/006 |
| RF-14, RF-15 | Must | Regras do projeto e pedido do titular (/impeccable) |
| RF-05, RF-07, RF-09, RF-13 | Should | Polimento do fluxo |
| RF-07a, RF-07b, RF-11a, RF-11b | Must | Decisão do titular: as 7 abas completas nesta feature (Q1) |
| RF-07c | Should | Efeito inferido (lacunas 3 e 9 da elicitação) |
| Frentes e gavetas por subvão da 006 | Won't (nesta feature) | Feature seguinte (Q2) |
| Barra de ferramentas do Construtor (zoom, pan, régua) | Won't | A vista do editor já tem zoom pela roda; o resto do Blender cobre |

## 9. Esclarecimentos

### Sessão 2026-10-08

- **Q:** Escopo desta feature? **R:** (d) Tudo de uma vez: as 7 abas completas. → RN-01, RN-02, RN-07a a RN-07c,
  RN-13a, RN-13b
- **Q:** Onde Gavetas e Portas são inseridas? **R:** (c) No vão da biblioteca agora; no subvão da 006 numa feature
  seguinte. → RN-11
- **Q:** O que o botão Aplicar faz? **R:** (a) Grava (um passo de desfazer), mantém o editor aberto e vira a nova
  referência do Cancelar. → RN-04
- **Q:** "Inserir invertido" na aba Portas? **R:** (a) Troca o lado da dobradiça. → RN-13
- **Q:** Recuo padrão do fundo "Inteiro Recuado"? **R:** Seguir a sugestão: 20 mm, editável. → RN-14

### Sessão 2026-10-08 (2), após a auditoria `audit/cross-check.md`

- **Q:** Itens de catálogo sem regra (Móveis, Distanciadores, Sem Divisória, Gavetões, Internas, Blum)? **R:** (a)
  Definir e implementar. → RN-10a, RN-12, RF-09a, RF-10a (A002)
- **Q:** Sem vão escolhido, o botão Inserir? **R:** (a) Desabilitado com "Selecione um vão na vista". → RN-05 (A001)
- **Q:** Pés plásticos e a lista de ferragens? **R:** (b) Criar agora uma lista simples de ferragens no plano de corte e
  na exportação. → RN-07a, RN-16, RF-16 (A005)
- **Q:** Puxador nas gavetas? **R:** (a) A aba Gavetas também tem escolha de puxador. → RN-12, RF-10a (A009)
- **Q:** Nomes das abas em inglês? **R:** (a) Structure, Divisions, Drawers, Interior, Doors, Sliding, Backs. → RF-14
  (A004)
- Correções de texto sem pergunta: cenário com as 7 abas (A003); origem do "tipo do armário" (RN-08, A006).

## 10. Lacunas

- 🔴 **Risco de escopo (registrado a pedido do titular, Q1):** as 7 abas completas juntam quatro motores de geometria
  novos: componentes extras, painel/eletro, porta de correr com trilhos e fundo recuado. Somam-se às abas que
  reaproveitam 003/006. É a maior feature do projeto até aqui. O `/reversa-plan` deve dividir a entrega em
  incrementos que funcionem sozinhos (fluxo → abas reaproveitadas → Internos → Deslizantes → componentes extras), para
  que cada parte possa ir para o projeto mesmo que as seguintes atrasem.
- 🟡 Inferências sem marcador:
  - geometria de cada componente extra (RN-07a);
  - efeito de Número de vãos, Posição e Movimentação (RN-07b, RN-07c);
  - medidas de catálogo dos eletros e geometria de Apoios e Pistões (RN-13a);
  - trilhos, número de folhas e sobreposição dos deslizantes (RN-13b);
  - distribuição igual na inserção múltipla e nas gavetas (RN-09, RN-12).
- 🟡 A lista de ferragens (RN-16) muda a exportação de produção: o contrato
  `_reversa_forward/003-modulos-agregados-reposicionar/interfaces/cut-plan-json.md` precisa de versão nova (campo
  opcional) no `/reversa-plan`.
- 🟡 Lacunas da elicitação herdadas: unidade (o projeto já usa a unidade da cena), atalhos, regras finas de
  basculante (itens 11 e 13 da seção 13 da elicitação).

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-10-08 | Versão inicial gerada por `/reversa-requirements` | reversa |
| 2026-10-08 | Sessão de esclarecimentos: 5 respostas integradas; escopo ampliado para as 7 abas (RN-01, RN-02, RN-04, RN-07a–c, RN-11, RN-13, RN-13a, RN-13b, RN-14) | reversa-clarify |
| 2026-10-08 | Sessão de esclarecimentos 2 (auditoria): 5 respostas; RN-10a, RN-16, RF-09a, RF-10a, RF-16; correções A003, A004, A006 | reversa-clarify |
