# Requirements: Editor de armário reformulado em abas (Estrutura e Divisão)

> Identificador: `006-editor-armario-abas`
> Data: `2026-10-08`
> Pasta da extração reversa: `_reversa_sdd/`
> Origem: pedido do titular ("o editor de armário deve ser reformulado: abas, completíssimo mas bem simples; aba
> Estrutura com dimensões externas e componentes externos editáveis/removíveis; aba Divisão com chapas verticais e
> horizontais de MDF/MDP, ocupando todo o espaço, com recuo na frente/atrás escolhido antes de adicionar"). O desenho
> visual do painel será feito depois com `/impeccable`.
> Confidência: 🟢 CONFIRMADO, 🟡 INFERIDO, 🔴 LACUNA / DÚVIDA

## 1. Resumo executivo

O editor de armário da 004 junta medidas, lista de componentes, personalização, mensagens e ajustes num painel único e
longo. O projetista não consegue, nele, tirar a lateral ou o tampo do armário nem acrescentar uma divisória ou prateleira
fixa no lugar que quer: as divisões internas de hoje só aceitam uma *quantidade* com espaçamento igual. Esta feature
reorganiza o editor em **abas** e entrega duas abas novas: **Estrutura** (medidas externas e componentes externos,
cada um editável e removível) e **Divisão** (chapas verticais e horizontais de vão inteiro, no material e espessura
configurados, com recuo na frente e atrás escolhido pelo usuário).

## 2. Contexto a partir do legado

| Fonte | Trecho relevante | Confidência |
|-------|------------------|-------------|
| `_reversa_sdd/domain.md#1.1 Entidades do Ambiente 3D` | Módulo = armário paramétrico composto por painéis de MDF/MDP | 🟢 |
| `_reversa_sdd/domain.md#1.2 Entidades de Produção` | Chapa, refilo, kerf e veio: toda peça do módulo vira peça do plano de corte | 🟢 |
| `_reversa_sdd/architecture.md#3. Modelo de Entidades e Relacionamentos (ERD)` | `CABINET-PROPERTIES` com largura, altura, profundidade e espessura | 🟢 |
| `_reversa_sdd/code-analysis.md#1.4 Parâmetros de Módulos de Mobiliário` | Parâmetros do módulo `btm` | 🟢 |
| `_reversa_forward/004-editor-armario-grudar/requirements.md#4` (RN-01..RN-04) | Editor trabalha em rascunho: nada muda antes de Confirmar, Cancelar restaura, Confirmar é um único desfazer; mensagens com gravidade; erro bloqueia Confirmar | 🟢 |
| `caffmob_draw/cabinet_editor/panels.py` | Editor atual: painéis Medidas, Componentes, Personalizar (Frentes, Puxadores, Materiais, Divisões internas), Mensagens, Ajustes automáticos, Confirmar | 🟢 |
| `caffmob_draw/customize/spec.py` (`Interior`) | Divisões internas de hoje = contagem de prateleiras/divisórias/gavetas por vão, espaçamento igual, até 10 divisórias e 20 prateleiras | 🟢 |
| `caffmob_draw/data/dimension_schema.py` (`COMPONENTS`, `SHEET_FIELDS`, `MATERIALS`) | Configurador de Dimensões guarda, **por linha** (Cozinhas, Dormitórios, Banheiros, Salas, Escritórios) e **por componente** (Lateral, Divisória, Base, Fundo, Tampo, Prateleira…), o material (MDF, MDP, Compensado, OSB, Vidro, Outro) e a espessura | 🟢 |
| `caffmob_draw/standards/sync.py` (`_tag_lines`) | Cada módulo tem uma linha (`btm_line`): frameless → Cozinhas, closets → Dormitórios por padrão | 🟢 |
| `caffmob_draw/product_libraries/closets/props_closets.py` (`remove_bottom`) | Só os closets já têm "remover base"; nas outras bibliotecas não há chave nativa para tirar tampo, base, fundo ou lateral | 🟡 |

## 3. Personas e cenários de uso

| Persona | Objetivo | Cenário-chave |
|---------|----------|---------------|
| Projetista de interiores | Ajustar a caixa do armário | Abre o editor de um balcão de 800 × 720 × 560 mm, na aba Estrutura remove a lateral direita (vai encostar em outro módulo) e troca a espessura do tampo de 15 para 18 mm |
| Projetista de interiores | Dividir o interior onde quer | Na aba Divisão escolhe "Vertical", marca "recuo na frente", adiciona, digita 400 mm da lateral esquerda, depois adiciona uma horizontal sem recuo a 360 mm da base |
| Marceneiro (produção) | Receber peças corretas | Gera o plano de corte e vê a divisória com a profundidade já descontada do recuo e no material da linha (MDP 15 mm), e não vê a lateral removida |

## 4. Regras de negócio novas ou alteradas

**Glossário desta feature.** *Componente externo*: chapa que fecha a caixa do armário: **tampo** (chapa de cima),
**base** (chapa de baixo), **fundo** (chapa de trás), **lateral esquerda** e **lateral direita**, nomes iguais aos do
Configurador de Dimensões. *Vão interno*: espaço livre entre as faces internas dos componentes externos.
*Divisão*: chapa que o usuário acrescenta dentro do vão: **vertical** (em pé, separa esquerda e direita) ou
**horizontal** (deitada, separa cima e baixo). *Recuo*: distância que a divisão fica afastada da borda da frente ou do
fundo do vão interno. *Linha*: a linha de produto do módulo no Configurador (Cozinhas, Dormitórios…).

**A. Editor em abas**

1. **RN-01:** O editor de armário organiza as ferramentas em abas. As duas primeiras, nesta ordem, são **Estrutura** e
   **Divisão**. Nenhuma função do editor da 004 deixa de existir: Frentes, Puxadores, Materiais, Mensagens, Ajustes
   automáticos, Desfazer/Refazer, Confirmar, Cancelar, Fechar e Salvar como módulo continuam acessíveis. 🟡
   - Origem no legado: `caffmob_draw/cabinet_editor/panels.py`
   - Tipo: alterada
2. **RN-02:** Confirmar, Cancelar e as mensagens funcionam em **todas** as abas e ficam sempre visíveis: o rascunho,
   o desfazer único e o bloqueio por erro da 004 valem para as mudanças das duas abas novas. 🟢
   - Origem no legado: `_reversa_forward/004-editor-armario-grudar/requirements.md#4` (RN-01, RN-03)
   - Tipo: alterada

**B. Aba Estrutura**

3. **RN-03:** A aba Estrutura mostra as dimensões externas (largura, altura, profundidade) do armário, editáveis com a
   faixa permitida, e a lista dos componentes externos com, para cada um: nome, medidas da chapa (calculadas),
   material e espessura. 🟡
   - Tipo: nova
4. **RN-04:** Cada componente externo pode ser **editado** (material e espessura) e **removido**. Componente removido
   continua na lista, marcado como removido, com a ação **Restaurar**. Componente removido some da vista e do plano
   de corte. 🟡
   - Origem no legado: `_reversa_sdd/domain.md#1.2 Entidades de Produção`
   - Tipo: nova
5. **RN-05:** O valor inicial de material e espessura de cada componente externo é o do Configurador de Dimensões
   para a linha do módulo. Um valor editado no armário vale só para esse armário e é marcado como "alterado neste
   armário". 🟡
   - Tipo: nova
6. **RN-06:** Ao remover um componente externo, o usuário escolhe como o armário se ajusta, com três modos:
   **Manter tudo** (padrão: medidas externas e as outras chapas ficam onde estão, só a chapa removida some e fica a
   abertura), **Estender as vizinhas** (medidas externas iguais, as chapas vizinhas avançam até a borda e o vão
   interno cresce pela espessura retirada) e **Reduzir o armário** (medidas externas diminuem pela espessura retirada,
   vão interno igual). Restaurar desfaz o ajuste do modo usado. 🟢 (clarify 2026-10-08, Q3)
   - Tipo: nova
7. **RN-07:** Se a biblioteca do módulo não conseguir remover ou editar um componente, a ação aparece desabilitada com
   o motivo (mesmo padrão das seções indisponíveis da 003). 🟡
   - Origem no legado: `_reversa_forward/003-modulos-agregados-reposicionar/requirements.md#5`
   - Tipo: nova

**C. Aba Divisão**

8. **RN-08:** Antes de adicionar, o usuário escolhe a **orientação** (vertical ou horizontal) e marca, de forma
   independente, **recuo na frente** (sim/não) e **recuo atrás** (sim/não). As escolhas ficam lembradas para a próxima
   divisão enquanto o editor estiver aberto. 🟢 (pedido do titular)
   - Tipo: nova
9. **RN-09:** Uma divisão ocupa o espaço inteiro do vão em que entra: a **vertical** vai da face de cima à face de
   baixo do vão e de frente a fundo; a **horizontal** vai da face esquerda à face direita do vão e de frente a fundo.
   Só os recuos marcados reduzem a profundidade. Quando já existem divisões, "o vão" é o **subvão escolhido** pelo
   usuário: o espaço limitado pelas faces dos componentes externos e das divisões que já existem (ex.: uma horizontal
   só no lado esquerdo de uma vertical). Sem divisões, o subvão é o vão interno inteiro. 🟢 (clarify 2026-10-08, Q1)
   - Tipo: nova
10. **RN-10:** O material e a espessura da divisão vêm do componente **Divisória** do Configurador de Dimensões na
    linha do módulo, seja qual for o material ativo ali (MDF, MDP ou outro), tanto para a vertical quanto para a
    horizontal. A aba mostra esse material e espessura antes de adicionar. 🟢 (clarify 2026-10-08, Q5)
    - Tipo: nova
11. **RN-11:** A divisão nova entra no **meio** do subvão. Depois de adicionada, a posição pode ser digitada como
    distância da face esquerda do subvão (vertical) ou da face de baixo do subvão (horizontal), na unidade do
    projeto. 🟢 (clarify 2026-10-08, Q4)
    - Tipo: nova
12. **RN-12:** Cada divisão já adicionada aparece numa lista da aba Divisão e pode ter posição, recuos, material e
    espessura editados, ou ser removida. 🟡
    - Tipo: nova
13. **RN-13:** Recuo da frente e recuo de trás têm medidas **separadas**. Cada um começa com um valor padrão único
    (20 mm) e pode ser editado em cada divisão; desmarcado = 0. 🟢 (clarify 2026-10-08, Q2); valor padrão de 20 mm 🟡
    (exemplo da pergunta, aceito sem número explícito)
    - Tipo: nova
14. **RN-14:** Nenhum subvão pode ficar com menos de 50 mm livres entre faces; posição que viole isso gera **erro**
    (bloqueia Confirmar) com a faixa permitida. Recuo que deixe a chapa com menos de 50 mm de profundidade também é
    erro. 🟡
    - Origem no legado: `_reversa_forward/004-editor-armario-grudar/requirements.md#4` (RN-03)
    - Tipo: nova
15. **RN-15:** Divisões entram no plano de corte como peças do módulo, com o material, a espessura e a profundidade já
    descontada dos recuos, e com o veio e as fitas do componente Divisória da linha. 🟡
    - Origem no legado: `_reversa_sdd/domain.md#1.2 Entidades de Produção`
    - Tipo: nova
16. **RN-16:** Remoções de componentes, edições e divisões ficam gravadas no módulo: sobrevivem a salvar e reabrir o
    projeto, a mudar as dimensões externas (as divisões mantêm a posição relativa à face de referência e são
    reajustadas ao novo vão) e a "Salvar como módulo". 🟡
    - Origem no legado: `caffmob_draw/customize/spec.py` (personalização gravada por instância)
    - Tipo: nova

## 5. Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de aceite | Confidência |
|----|-----------|------------|--------------------|-------------|
| RF-01 | Editor de armário em abas, com Estrutura e Divisão como as duas primeiras (RN-01) | Must | Ao abrir o editor, as abas aparecem e a aba Estrutura vem aberta | 🟡 |
| RF-02 | Toda função do editor da 004 continua acessível depois da reorganização (RN-01) | Must | Cada uma das 10 ações listadas em RN-01 é alcançável a partir do editor aberto | 🟡 |
| RF-03 | Confirmar, Cancelar e o indicador de erros ficam visíveis em qualquer aba (RN-02) | Must | Trocando de aba, os três continuam na tela; com erro, Confirmar fica bloqueado em todas | 🟢 |
| RF-04 | Aba Estrutura mostra e edita largura, altura e profundidade externas com faixa (RN-03) | Must | Valor digitado fora da faixa vira erro; dentro dela a prévia atualiza | 🟢 |
| RF-05 | Aba Estrutura lista tampo, base, fundo, lateral esquerda e lateral direita com medidas, material e espessura (RN-03) | Must | Os 5 componentes aparecem para um módulo que tem os 5; medidas batem com a peça na vista em ±0,5 mm | 🟡 |
| RF-06 | Editar material e espessura de cada componente externo (RN-04, RN-05) | Must | Trocar o tampo de 15 para 18 mm muda a peça na prévia e marca "alterado neste armário" | 🟡 |
| RF-07 | Remover e restaurar cada componente externo, escolhendo o modo de ajuste: Manter tudo (padrão), Estender as vizinhas ou Reduzir o armário (RN-04, RN-06) | Must | Removido: some da prévia e, após Confirmar, do plano de corte; cada modo produz as medidas descritas em RN-06; Restaurar devolve a peça e as medidas iguais às de antes | 🟢 |
| RF-08 | Ação indisponível pela biblioteca aparece desabilitada com o motivo (RN-07) | Should | Em módulo cuja biblioteca não remove o fundo, o botão de remover o fundo está desabilitado com texto do motivo | 🟡 |
| RF-09 | Escolher orientação e recuos (frente, atrás, cada um com medida própria, padrão 20 mm) antes de adicionar uma divisão (RN-08, RN-13) | Must | As escolhas estão disponíveis antes do botão Adicionar e a divisão criada as respeita; recuo desmarcado = 0 | 🟢 |
| RF-10 | Escolher o subvão e a divisão ocupa esse subvão inteiro na sua orientação (RN-09) | Must | Vertical: altura = altura do subvão; horizontal: largura = largura do subvão; profundidade = profundidade do subvão menos os recuos marcados; sem divisões, subvão = vão interno | 🟢 |
| RF-11 | Material e espessura da divisão (vertical ou horizontal) vêm do componente Divisória da linha do módulo e são mostrados antes de adicionar (RN-10) | Must | Com Divisória = MDP 15 mm na linha Dormitórios, um closet recebe divisão MDP 15 mm, vertical ou horizontal | 🟢 |
| RF-12 | Divisão nova entra no meio do subvão e a posição é editável por número (RN-11) | Must | Subvão de 768 mm: vertical entra com a face esquerda a (768 − espessura)/2; digitar 400 mm move a chapa para 400 mm da face esquerda do subvão | 🟢 |
| RF-13 | Lista de divisões com edição de posição, recuos (medidas da frente e de trás), material, espessura e remoção (RN-12, RN-13) | Must | Cada divisão adicionada aparece na lista; remover tira a chapa da prévia | 🟡 |
| RF-14 | Validação de subvão mínimo e profundidade mínima (RN-14) | Must | Posição que deixa subvão < 50 mm gera erro com a faixa permitida e bloqueia Confirmar | 🟡 |
| RF-15 | Divisões e componentes externos no plano de corte (RN-15) | Must | Após Confirmar, a lista de peças tem cada divisão com material, espessura e profundidade descontada; componente removido não aparece | 🟡 |
| RF-16 | Persistência das mudanças (RN-16) | Must | Salvar, fechar e reabrir o projeto mantém remoções, edições e divisões; mudar a largura externa reajusta as divisões ao vão novo | 🟡 |
| RF-17 | Textos novos em pt-BR e en-US | Must | Com a interface em inglês, as abas aparecem como "Structure" e "Divisions" e não sobra texto em português | 🟢 |

## 6. Requisitos Não Funcionais

| Tipo | Requisito | Evidência ou justificativa | Confidência |
|------|-----------|----------------------------|-------------|
| Desempenho | A prévia atualiza em até 0,5 s depois de adicionar, mover ou remover uma divisão, num armário com até 20 divisões | O editor da 004 recalcula a prévia a cada mudança; 20 = limite de prateleiras de `customize/spec.py` | 🟡 |
| Usabilidade | Cada aba cabe sem rolagem numa barra lateral de 1080 px de altura com até 5 divisões listadas ("completíssimo mas bem simples") | Pedido do titular | 🟡 |
| Confiabilidade | Cancelar devolve o módulo idêntico ao de antes de abrir o editor, inclusive componentes removidos e divisões | `_reversa_forward/004-editor-armario-grudar/requirements.md#4` (RN-01) | 🟢 |
| Confiabilidade | Confirmar gera um único passo de desfazer, que desfaz todas as mudanças das abas | 004 RN-01 | 🟢 |
| Compatibilidade | Funciona no alvo do projeto (Blender 5.2) para os módulos das bibliotecas suportadas pela 003 | `CLAUDE.md` (alvo 5.2) | 🟢 |
| Observabilidade | Cada erro de validação tem código, componente, parâmetro, valor e faixa (padrão da 004) | 004 RN-03 | 🟢 |

## 7. Critérios de Aceitação

```gherkin
Cenário: Abrir o editor em abas
  Dado um balcão inserido no projeto
  Quando o projetista abre o editor de armário
  Então vê as abas "Estrutura" e "Divisão", nessa ordem, com "Estrutura" aberta
  E vê Confirmar e Cancelar

Cenário: Funções antigas continuam acessíveis
  Dado o editor de armário aberto
  Quando o projetista procura Frentes, Puxadores, Materiais, Mensagens, Ajustes automáticos e Salvar como módulo
  Então encontra cada uma delas no editor

Cenário: Ver e editar as dimensões externas
  Dado o editor aberto na aba Estrutura de um balcão de 800 x 720 x 560 mm
  Quando o projetista digita 900 mm na largura
  Então a prévia mostra o balcão com 900 mm de largura

Cenário: Listar e editar componentes externos
  Dado o editor aberto na aba Estrutura de um balcão com tampo de 15 mm
  Quando o projetista muda a espessura do tampo para 18 mm
  Então a prévia mostra o tampo com 18 mm
  E o tampo aparece marcado como "alterado neste armário"

Cenário: Remover e restaurar a lateral direita
  Dado o editor aberto na aba Estrutura de um balcão com as duas laterais
  Quando o projetista remove a lateral direita
  Então a lateral direita some da prévia e aparece na lista como removida
  E, no modo padrão Manter tudo, a largura externa e as outras chapas não mudam
  Quando o projetista clica em Restaurar na lateral direita
  Então a lateral volta igual à de antes

Cenário: Remover a lateral direita no modo Estender as vizinhas
  Dado o editor aberto na aba Estrutura de um balcão de 800 mm de largura com laterais de 15 mm
  Quando o projetista remove a lateral direita escolhendo "Estender as vizinhas"
  Então a largura externa continua 800 mm
  E tampo e base avançam até a borda direita, e o vão interno fica 15 mm mais largo

Cenário: Remover a lateral direita no modo Reduzir o armário
  Dado o editor aberto na aba Estrutura de um balcão de 800 mm de largura com laterais de 15 mm
  Quando o projetista remove a lateral direita escolhendo "Reduzir o armário"
  Então a largura externa passa a 785 mm e o vão interno não muda

Cenário: Componente removido sai do plano de corte
  Dado um balcão com a lateral direita removida e confirmada
  Quando o projetista gera o plano de corte
  Então nenhuma peça "Lateral direita" desse balcão aparece na lista de peças

Cenário: Ação não suportada pela biblioteca
  Dado um módulo cuja biblioteca não permite remover o fundo
  Quando o projetista abre a aba Estrutura
  Então o botão de remover o fundo aparece desabilitado com o motivo

Cenário: Adicionar divisão vertical com recuo na frente
  Dado o editor aberto na aba Divisão de um armário com vão interno de 768 x 690 x 540 mm
  E a Divisória da linha do módulo configurada como MDP 15 mm
  E o recuo na frente marcado e o recuo atrás desmarcado
  Quando o projetista escolhe "Vertical" e clica em Adicionar
  Então surge no meio do vão uma chapa MDP de 15 mm com 690 mm de altura
  E a profundidade da chapa é 540 mm menos o recuo da frente
  E a divisão aparece na lista da aba Divisão

Cenário: Adicionar divisão horizontal sem recuo
  Dado o editor aberto na aba Divisão de um armário com vão interno de 768 x 690 x 540 mm
  E nenhum recuo marcado
  Quando o projetista escolhe "Horizontal" e clica em Adicionar
  Então surge uma chapa de 768 x 540 mm no meio da altura do vão

Cenário: Adicionar divisão só num subvão
  Dado um armário com uma divisão vertical que separa o vão em esquerdo e direito
  Quando o projetista escolhe o subvão esquerdo, "Horizontal" e clica em Adicionar
  Então surge uma chapa horizontal só no subvão esquerdo, da lateral esquerda até a divisão vertical
  E o subvão direito não muda

Cenário: Recuos com medidas diferentes
  Dado o editor aberto na aba Divisão de um armário com vão interno de 540 mm de profundidade
  E o recuo na frente marcado com 20 mm e o recuo atrás marcado com 10 mm
  Quando o projetista adiciona uma divisão vertical
  Então a chapa tem 510 mm de profundidade, afastada 20 mm da frente e 10 mm do fundo

Cenário: Mover uma divisão por número
  Dado uma divisão vertical no vão de 768 mm
  Quando o projetista digita 400 mm na posição
  Então a face esquerda da divisão fica a 400 mm da face interna da lateral esquerda

Cenário: Posição que deixa subvão pequeno demais
  Dado uma divisão vertical num vão de 768 mm
  Quando o projetista digita 20 mm na posição
  Então aparece um erro com a faixa permitida
  E Confirmar fica bloqueado

Cenário: Remover uma divisão
  Dado um armário com duas divisões na lista
  Quando o projetista remove a primeira
  Então ela some da prévia e da lista, e a outra continua no lugar

Cenário: Cancelar desfaz tudo
  Dado o editor aberto, com a lateral direita removida e duas divisões adicionadas
  Quando o projetista clica em Cancelar
  Então o módulo volta exatamente como estava antes de abrir o editor

Cenário: Divisões no plano de corte
  Dado um armário com uma divisão vertical com recuo na frente, confirmada
  Quando o projetista gera o plano de corte
  Então a divisão aparece como peça com o material e a espessura da Divisória da linha e a profundidade descontada do recuo

Cenário: Persistência ao reabrir e ao redimensionar
  Dado um armário com uma lateral removida e uma divisão horizontal a 360 mm da base, confirmados
  Quando o projetista salva, reabre o projeto e muda a largura externa de 800 para 1000 mm
  Então a lateral continua removida
  E a divisão horizontal continua a 360 mm da base, agora com a largura do vão novo

Cenário: Interface em inglês
  Dado a interface configurada em en-US
  Quando o projetista abre o editor de armário
  Então as abas aparecem como "Structure" e "Divisions"
```

## 8. Prioridade MoSCoW

| Item | MoSCoW | Justificativa |
|------|--------|---------------|
| RF-01, RF-02, RF-03 | Must | Base da reformulação; sem RF-02 a feature remove funções da 004 |
| RF-04, RF-05, RF-06, RF-07 | Must | Aba Estrutura pedida pelo titular |
| RF-08 | Should | Necessário porque nem toda biblioteca remove todas as peças; sem ele o botão falha em silêncio |
| RF-09 a RF-14 | Must | Aba Divisão pedida pelo titular |
| RF-15, RF-16 | Must | Sem plano de corte e persistência a mudança não chega à produção |
| RF-17 | Must | Regra do projeto: interface completa em pt-BR e en-US (commit 53f594c) |
| RNF de desempenho | Should | Prévia lenta prejudica o uso, mas não bloqueia a entrega |
| RNF de usabilidade | Should | "Bem simples" é objetivo de desenho; será refinado no `/impeccable` |
| Rodapé, travessas, tamponamento e prateleiras ajustáveis na aba Estrutura/Divisão | Won't (nesta feature) | Fora do pedido; candidatos a features seguintes |

## 9. Esclarecimentos

### Sessão 2026-10-08

- **Q:** Quando o armário já tem divisões, até onde vai uma divisão nova? **R:** (a) Só no subvão escolhido, entre as
  divisões que já existem. → RN-09, RF-10
- **Q:** Qual a medida do recuo quando marcado? **R:** (a) Valor padrão único (20 mm), editável em cada divisão, frente
  e trás com medidas separadas. → RN-13, RF-09, RF-13
- **Q:** Ao remover tampo, base ou lateral, o que acontece com as medidas? **R:** (c) Medidas e demais chapas ficam
  onde estão, como padrão, **com opção** de (a) estender as vizinhas ou (b) reduzir o armário. → RN-06, RF-07
- **Q:** Onde a divisão nova aparece ao clicar em Adicionar? **R:** (a) No meio do subvão; depois digita-se a
  posição. → RN-11, RF-12
- **Q:** Divisão horizontal e vertical usam a mesma configuração de chapa? **R:** (a) As duas usam o componente
  "Divisória" do Configurador de Dimensões. → RN-10, RF-11

## 10. Lacunas

- 🟡 Valor padrão do recuo = 20 mm veio do exemplo da pergunta; confirmar se o titular quiser outro (RN-13).
- 🟡 Inferências ainda não confirmadas: subvão mínimo de 50 mm (RN-14); funções da 004 que não são Estrutura nem
  Divisão ficam em outras abas do editor (RN-01); como o subvão é escolhido (na lista ou clicando na vista) fica para o
  `/reversa-plan` e o `/impeccable`.
- 🟡 Risco técnico (para o `/reversa-plan`): só os closets têm "remover base" nativo; tirar tampo, fundo e laterais
  nas outras bibliotecas, e os modos "Estender as vizinhas" e "Reduzir o armário", exigem mecanismo novo.

## 11. Histórico de alterações

| Data | Alteração | Autor |
|------|-----------|-------|
| 2026-10-08 | Versão inicial gerada por `/reversa-requirements` | reversa |
| 2026-10-08 | Sessão de esclarecimentos: 5 respostas integradas (RN-06, RN-09, RN-10, RN-11, RN-13) | reversa-clarify |
