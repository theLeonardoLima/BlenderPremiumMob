# Elicitação de Requisitos — Construtor de Armários
## Reanálise detalhada baseada em vídeo e capturas de tela

**Produto:** ELÊ DE AMBIENTES — Promob Plus Enterprise 5.60.46.6  
**Janela observada:** `Construtor de Armários`  
**Vídeo:** `Gravação de Tela 2026-10-08 151417.mp4`  
**Capturas:** 20 imagens extraídas de `EDITOR DE ARMÁRIO.zip`  
**Versão:** 2.0 — reanálise baseada em evidências visuais  
**Objetivo:** transformar o comportamento observável do editor em uma especificação textual suficientemente completa para reconstrução, implementação, testes e homologação sem depender das imagens.

> **Escopo de evidência.** As capturas permitiram confirmar rótulos, abas, medidas, opções de catálogo, estados de seleção e controles. O vídeo não foi decodificado quadro a quadro neste ambiente; por isso, sequência temporal fina, cliques intermediários, atalhos e mensagens não visíveis nas capturas continuam classificados como lacunas. As capturas nomeadas com “TELA INICIAL”, “DIVISOES”, “GAVETAS”, “INTERNOS”, “PORTAS”, “DESLIZANTES” e “FUNDO” foram tratadas como evidência visual direta.

---

## 1. Convenção de confiança

- 🟢 **CONFIRMADO** — legível diretamente nas capturas ou derivado de um controle visual inequívoco.
- 🟡 **INFERIDO** — comportamento necessário para explicar a interface ou recomendado para implementação compatível.
- 🔴 **LACUNA** — não determinável somente pelas evidências fornecidas.

Quando uma regra é confirmada na existência do controle, mas seu efeito exato não aparece, o controle é 🟢 e o comportamento é 🟡/🔴.

---

## 2. Evidências confirmadas

### 2.1 Aplicação e janela

- 🟢 A aplicação hospedeira é **ELÊDE AMBIENTES — Promob Plus Enterprise — 5.60.46.6**.
- 🟢 A janela especializada chama-se **Construtor de Armários**.
- 🟢 O construtor é aberto sobre um ambiente 3D do Promob; a captura 15:18:10 mostra o ambiente ao fundo.
- 🟢 A tela possui barra de título, barra de ferramentas, área de desenho técnico e painel lateral de configuração.
- 🟢 A janela possui os botões **OK**, **Cancelar** e **Aplicar**.
- 🟢 O botão **Aplicar** aparece desabilitado em várias capturas, indicando que sua habilitação depende de alteração ou estado específico.
- 🟢 A barra inferior exibe **Selecionado: (nenhum)** ou **Selecionado: Vão**.

### 2.2 Abas principais observadas

- 🟢 **Estrutura**
- 🟢 **Divisões**
- 🟢 **Gavetas**
- 🟢 **Internos**
- 🟢 **Portas**
- 🟢 **Deslizantes**
- 🟢 **Fundos**

### 2.3 Tipo e medidas observadas

Na tela de estrutura:

- 🟢 **Tipo:** `Torre p/ Eletros`
- 🟢 **Número de vãos:** `1`
- 🟢 **Largura total:** `800`
- 🟢 **Altura:** `2250`
- 🟢 **Profundidade:** `550`
- 🟢 A vista exibe largura externa superior de `800`.
- 🟢 A vista exibe altura externa de `2250`.
- 🟢 A vista exibe uma medida inferior de `770`, coerente com largura interna após duas laterais de `15 mm`.
- 🟢 Na configuração com o vão selecionado aparecem medidas verticais `340` e `1880`, indicando divisão do espaço em uma área superior e outra inferior.
- 🟢 A unidade não aparece escrita nas capturas, mas os valores `15`, `50`, `150`, `800`, `2250` e `550` são apresentados como medidas dimensionais do móvel. 🔴 A unidade deve ser confirmada; a hipótese mais provável é milímetro.

### 2.4 Componentes estruturais observados

A árvore de componentes da aba **Estrutura** mostra:

- 🟢 `Lateral Esquerda 15mm`
- 🟢 `Lateral Direita 15mm`
- 🟢 `Divisória`
- 🟢 `Base Inferior 15mm`
- 🟢 `Base Superior 15mm`
- 🟢 `Base Superior Recuada 15mm`
- 🟢 `Pés Plásticos`
  - `Posição 01` — valor `150`
  - `Posição 02` — valor `150`
  - `Posição 03` — valor `150`
  - `Posição 04` — valor `150`
- 🟢 `Rodapés`
  - `Frontal`
  - `Esquerdo`
  - `Direito`
- 🟢 `Rodapés Granito`
- 🟢 `Fechamentos` — valor observado `50`
- 🟢 `Vistas`
  - `Frontal` — `150`
  - `Esquerda` — `150`
  - `Direita` — `150`
- 🟢 `Vistas (alto)`
  - `Esquerda`
  - `Direita`
  - `Frontal`

A árvore possui caixas de seleção e nós expansíveis. Isso confirma que a composição é configurável por componente, não apenas por um único modelo monolítico.

### 2.5 Controles de posicionamento observados

- 🟢 Grupo **Posição**.
- 🟢 Modo exibido: **Livre**.
- 🟢 Campos **Cota anterior**, **Cota inferior**, **Cota posterior** e **Cota superior**.
- 🟢 Os campos aparecem com valor `0` na tela inicial.
- 🟢 Na tela observada, os campos de posição estão visualmente desabilitados enquanto o modo é Livre ou enquanto nenhum elemento apropriado está selecionado. 🔴 Confirmar regra exata de habilitação.

### 2.6 Grupo de movimentação

- 🟢 Painel **Movimentação**.
- 🟢 Campo **Passo inicial** com valor `0`.
- 🟢 Campo **Passo** com valor `10`.
- 🟢 O painel possui controle de expansão/recolhimento.
- 🟡 O passo provavelmente controla o incremento usado por movimentações dimensionais do componente selecionado.
- 🔴 Ação que consome o passo e unidade do incremento precisam ser confirmadas no vídeo.

---

## 3. Descrição completa da interface

### 3.1 Barra de ferramentas

A barra superior da janela contém ícones para ações de edição e navegação. Pelas capturas, são visíveis, em sequência aproximada:

- 🟢 novo/abrir ou ação inicial;
- 🟢 desfazer;
- 🟢 refazer, inicialmente desabilitado em alguns estados;
- 🟢 ferramenta de edição/seleção;
- 🟢 ferramenta de visualização ou enquadramento;
- 🟢 grade/medição;
- 🟢 seleção;
- 🟢 mão/pan;
- 🟢 zoom para ampliar;
- 🟢 zoom para reduzir;
- 🟢 zoom/enquadrar;
- 🟢 limpar/remover, aparentemente desabilitado quando nada está selecionado;
- 🟢 ajuda.

🔴 Os nomes e atalhos exatos dos ícones não são legíveis nas capturas. A implementação deve manter os comportamentos, mas não deve inventar atalhos.

### 3.2 Área gráfica

A área esquerda apresenta uma vista frontal ortográfica do armário com:

- 🟢 contorno externo;
- 🟢 prateleiras/divisões representadas por linhas horizontais azuis;
- 🟢 divisão vertical central;
- 🟢 dimensões externas;
- 🟢 regiões internas preenchidas em cinza;
- 🟢 linhas tracejadas indicando trajetórias/aberturas de portas ou projeções;
- 🟢 realce vermelho/translúcido para o vão selecionado;
- 🟢 realce roxo para uma região/componente selecionado em algumas telas;
- 🟢 realce verde para portas/linhas de abertura na aba Portas.

🟡 A área gráfica é simultaneamente visualização, superfície de seleção e editor de componentes.

### 3.3 Painel lateral

O painel lateral muda conforme a aba selecionada. Cada aba combina:

1. subabas ou filtros de catálogo;
2. lista visual de opções com miniaturas;
3. botão **Inserir**;
4. checkbox **Inserir invertido**, quando aplicável;
5. painel inferior de propriedades, que pode exibir **Não há propriedades disponíveis!**.

### 3.4 Rodapé e confirmação

- 🟢 **OK** confirma e fecha.
- 🟢 **Cancelar** abandona a janela ou as alterações conforme o estado.
- 🟢 **Aplicar** aplica sem necessariamente fechar e pode permanecer desabilitado.
- 🟢 A barra inferior informa o objeto selecionado.

---

## 4. Fluxo funcional reconstruído

### 4.1 Abertura

1. O usuário está em um ambiente do Promob.
2. O construtor é aberto para um armário/módulo existente ou novo.
3. O sistema carrega um móvel do tipo `Torre p/ Eletros`.
4. O editor calcula a vista frontal, dimensões e árvore de componentes.
5. A aba inicial é **Estrutura**.
6. Nenhum elemento específico pode estar selecionado inicialmente.
7. O botão Aplicar fica indisponível enquanto não há alteração aplicável.

### 4.2 Alteração de estrutura

1. O usuário acessa Estrutura.
2. Edita número de vãos, largura, altura ou profundidade.
3. O sistema recalcula o desenho.
4. A medida interna pode mudar em função de espessuras laterais, divisórias, recuos e componentes selecionados.
5. O usuário marca/desmarca itens da árvore.
6. O sistema adiciona/remove ou ativa/desativa o componente correspondente.
7. O estado passa a ter alteração pendente.
8. Aplicar fica disponível quando a alteração for válida.

### 4.3 Inserção de divisão

1. O usuário acessa **Divisões**.
2. Escolhe orientação **Vertical**, **Horizontal** ou **Inserção múltipla**.
3. Escolhe uma subcategoria:
   - Divisórias Móveis;
   - Divisórias Fixas;
   - Distanciador;
   - Sem Divisória.
4. Em Divisórias Fixas, pode escolher:
   - Com Recuo Frontal;
   - Sem Recuo Frontal.
5. O catálogo apresenta:
   - `Interna s/ Recuo — Tras 15mm`;
   - `Interna c/ Recuo — Tras 15mm`.
6. Em Distanciador, aparecem:
   - `Distanciador 15mm`;
   - `Distanciador Duplo 30mm`;
   - `Distanciador p/ Divisão 15mm`.
7. O usuário seleciona uma miniatura e insere.
8. O sistema deve recalcular o vão, atualizar dimensões e registrar a alteração.

### 4.4 Inserção de gavetas

1. O usuário seleciona um vão na vista.
2. A aba **Gavetas** fica ativa.
3. O sistema realça o vão selecionado em vermelho e mostra medidas `340` e `1880`.
4. O painel apresenta subabas:
   - Gavetas;
   - Gaveteiros;
   - Internas;
   - Blum.
5. Em **Opções de gavetas**, aparece `Gaveta c/ CF`, descrita como `Caixa Gaveta c/ Folha / Contra Frente`.
6. Em **Opções de frentes**, aparece `Reta`, descrita como `Frente Reta`.
7. Em **Opções de inserção**, o campo **Número de gavetas** aparece com valor `4` e controle incremental.
8. O usuário insere as gavetas.
9. O sistema deve distribuir as gavetas no vão, respeitando altura disponível, frente, caixa, folgas e configuração de catálogo.
10. O painel inferior pode informar **Não há propriedades disponíveis!** quando o item selecionado não tiver propriedade adicional editável.

### 4.5 Inserção de internos/eletros

1. O usuário acessa **Internos**.
2. As subabas visíveis são:
   - Painel p/ Eletros;
   - Biblioteca;
   - Apoios;
   - Pistões.
3. Em Painel p/ Eletros, existem filtros:
   - Externos;
   - Embutidos.
4. Opções visíveis:
   - `Painel Forno/Micro Externo`;
   - `Painel Forno Externo`;
   - `Painel Micro Externo`;
   - `Painel Cafeteira Externo`;
   - `Frontal Externo`;
   - `Forno`;
   - `Microondas`;
   - `Cafeteira`;
   - `Respiro`.
5. O usuário escolhe um item e insere no vão selecionado.
6. O sistema deve preservar a relação do eletro com o vão e validar compatibilidade dimensional.
7. O checkbox **Inserir invertido** aparece desabilitado nessa captura.

### 4.6 Inserção de portas

1. O usuário acessa **Portas**.
2. Os filtros superiores são:
   - Inferior;
   - Superior;
   - Alta;
   - Basculante.
3. Filtros de lado/escopo:
   - Ambas;
   - Inteira;
   - Esquerda;
   - Direita.
4. Estilos visíveis:
   - Reta;
   - Lisa;
   - Almofada;
   - Fresada;
   - Fresada 02;
   - Colonial;
   - Colonial 02;
   - Colonial 03;
   - Bicolor;
   - Gola Horizontal;
   - Gola Vertical;
   - Gola Vertical 2L.
5. O desenho mostra linhas de abertura tracejadas, indicando que o estilo de porta também afeta representação funcional.
6. O sistema deve impedir ou sinalizar incompatibilidade entre tipo de porta, vão e dimensão disponível.

### 4.7 Inserção de deslizantes

1. O usuário acessa **Deslizantes**.
2. O painel apresenta **Portas deslizantes**.
3. Há uma miniatura de porta e o texto de estilo, aparentemente `Lisa`.
4. O catálogo possui menu hierárquico de material/família:
   - Alumínio;
   - Madeira.
5. Sob Madeira, aparecem:
   - Lisa;
   - Reta;
   - Almofada;
   - Fresada;
   - Colonial;
   - Bicolor;
   - Gola Vertical;
   - Gola Vertical 2L;
   - Borda Alumínio;
   - Cava Vertical;
   - Chanfrada;
   - Country;
   - Perfil Y Vertical;
   - Perfil Y Vertical 2L;
   - Obispa — Pux Integrados;
   - Contatto — Pux Integrados;
   - Torralba — Pux Integrados;
   - Altero — Pux Integrados.
6. O checkbox **Inserir invertido** aparece desmarcado.
7. O sistema deve validar trilhos, número de folhas, sobreposição e sentido de abertura, ainda que esses campos não estejam visíveis nas capturas.

### 4.8 Inserção de fundos

1. O usuário acessa **Fundos**.
2. Subabas:
   - Inteiro;
   - Inteiro Recuado.
3. O checkbox **Inserir automaticamente** aparece marcado.
4. O catálogo apresenta `Fundo Inteiro 15mm`.
5. O sistema deve inserir ou recalcular o fundo automaticamente quando a opção estiver marcada.
6. A opção de inserir invertido aparece desabilitada.
7. O modo recuado deve alterar posição, profundidade ou relação do fundo com a estrutura.

### 4.9 Finalização

1. O usuário revisa a composição.
2. Seleciona Aplicar para manter a janela aberta ou OK para confirmar e fechar.
3. O sistema deve validar dependências, dimensões e compatibilidades.
4. Se houver erro bloqueante, deve impedir confirmação ou apresentar mensagem clara.
5. Cancelar deve restaurar o estado anterior, salvo confirmação específica para descartar alterações.

---

## 5. Requisitos funcionais confirmados e derivados

### RF-001 — Abrir construtor contextual

🟢 O sistema deve abrir a janela `Construtor de Armários` associada ao módulo/armário selecionado no ambiente.

**Aceite:** o tipo, medidas e componentes do armário atual são carregados na abertura.

### RF-002 — Exibir tipo do armário

🟢 O painel deve exibir o tipo atual, observado como `Torre p/ Eletros`.

**Aceite:** o tipo carregado deve determinar catálogo e regras disponíveis.

### RF-003 — Editar número de vãos

🟢 Deve existir o campo **Número de vãos** com controle numérico.

🟡 Ao alterar o valor, o sistema deve criar/remover vãos e recalcular divisórias e áreas dependentes.

### RF-004 — Editar dimensões globais

🟢 Devem existir os campos **Largura total**, **Altura** e **Profundidade**.

🟡 Alterações devem atualizar desenho, medidas internas, componentes, portas, gavetas e fundos.

### RF-005 — Exibir dimensões calculadas

🟢 O desenho deve exibir medidas externas e internas calculadas, como `800`, `2250`, `770`, `340` e `1880`.

🟡 Medidas calculadas devem ser somente leitura quando derivadas de parâmetros e devem indicar sua origem.

### RF-006 — Ativar/desativar componentes

🟢 A árvore de componentes deve permitir marcar/desmarcar itens.

**Aceite:** o estado do checkbox deve refletir a presença/ausência ou ativação/desativação do item no desenho.

### RF-007 — Hierarquia de componentes

🟢 Componentes agrupados devem possuir nós expansíveis, como Pés Plásticos, Rodapés, Vistas e Fechamentos.

**Aceite:** itens filhos podem ser configurados sem perder a relação com o grupo pai.

### RF-008 — Configurar posição

🟢 Deve existir o grupo Posição com modo Livre e cotas anterior, inferior, posterior e superior.

🟡 O sistema deve habilitar somente as cotas compatíveis com o modo e a seleção atual.

### RF-009 — Configurar movimentação

🟢 Deve existir Passo inicial e Passo, com valores observados `0` e `10`.

🟡 Movimentações devem obedecer ao passo configurado ou informar quando uma ação não puder ser aplicada.

### RF-010 — Inserir divisão vertical

🟢 Deve existir catálogo de divisórias verticais.

### RF-011 — Inserir divisão horizontal

🟢 Deve existir catálogo de divisórias horizontais.

### RF-012 — Inserção múltipla

🟢 Deve existir modo de **Inserção múltipla**.

🟡 O sistema deve definir quantidade, distribuição e critérios de espaçamento para inserção múltipla.

### RF-013 — Inserir divisória fixa ou móvel

🟢 O catálogo distingue Divisórias Móveis e Divisórias Fixas.

### RF-014 — Inserir divisória com ou sem recuo

🟢 Deve existir distinção entre Com Recuo Frontal e Sem Recuo Frontal.

### RF-015 — Inserir distanciadores

🟢 Devem existir Distanciador 15mm, Distanciador Duplo 30mm e Distanciador p/ Divisão 15mm.

### RF-016 — Selecionar vão alvo

🟢 O usuário deve conseguir selecionar um vão no desenho; a barra inferior exibe `Selecionado: Vão`.

**Aceite:** o vão selecionado deve ser realçado e os catálogos devem operar sobre ele.

### RF-017 — Inserir gavetas

🟢 Deve existir campo Número de gavetas e botão Inserir.

🟢 O valor observado é `4`.

🟡 O sistema deve distribuir as gavetas dentro do vão alvo.

### RF-018 — Escolher caixa e frente de gaveta

🟢 Deve ser possível escolher `Gaveta c/ CF` e frente `Reta`.

### RF-019 — Inserir internos/eletros

🟢 Deve existir catálogo de painéis, eletrodomésticos e acessórios internos.

### RF-020 — Separar externos e embutidos

🟢 A aba Internos possui filtros Externos e Embutidos.

### RF-021 — Inserir portas por região

🟢 A aba Portas permite filtrar Inferior, Superior, Alta e Basculante.

### RF-022 — Inserir portas por lado

🟢 A aba Portas permite filtrar Ambas, Inteira, Esquerda e Direita.

### RF-023 — Escolher estilo de porta

🟢 O catálogo deve apresentar estilos como Reta, Lisa, Almofada, Fresada, Colonial, Bicolor e Golas.

### RF-024 — Representar abertura

🟢 O desenho deve representar visualmente a abertura da porta por linhas de projeção/rotação.

### RF-025 — Inserir porta deslizante

🟢 Deve existir aba Portas deslizantes com famílias Alumínio e Madeira.

### RF-026 — Escolher acabamento de deslizante

🟢 O menu Madeira deve apresentar estilos e puxadores integrados observados.

### RF-027 — Inserir invertido

🟢 O sistema deve exibir checkbox Inserir invertido em catálogos aplicáveis.

🟡 Quando marcado, deve inserir o componente com orientação inversa, sem inverter apenas a aparência da miniatura.

### RF-028 — Inserir fundo automático

🟢 A aba Fundos deve possuir checkbox Inserir automaticamente, marcado na evidência.

### RF-029 — Fundo inteiro e recuado

🟢 Devem existir as opções Inteiro e Inteiro Recuado.

### RF-030 — Aplicar sem fechar

🟢 O botão Aplicar deve existir e refletir se há alteração aplicável.

### RF-031 — Confirmar ou cancelar

🟢 Os botões OK e Cancelar devem existir.

### RF-032 — Desfazer/refazer

🟢 A barra de ferramentas contém controles de desfazer/refazer.

🟡 O histórico deve incluir inserção, remoção, alteração de dimensão, seleção de catálogo e mudança de quantidade.

### RF-033 — Atualizar visualização

🟢 Cada alteração de composição deve atualizar a vista frontal e seus indicadores dimensionais.

### RF-034 — Informar ausência de propriedades

🟢 O painel deve exibir `Não há propriedades disponíveis!` quando o item não tiver propriedades adicionais disponíveis.

### RF-035 — Validar compatibilidade

🟡 O sistema deve validar se a opção escolhida é compatível com tipo, vão, medidas, material, abertura e posição.

### RF-036 — Manter rastreabilidade de alteração

🟡 O sistema deve registrar se o valor é digitado, derivado, aplicado automaticamente ou herdado de catálogo.

---

## 6. Regras de negócio

### RN-001 — Espessura estrutural

🟢 As laterais e bases observadas usam `15mm`. A largura interna observada `770` é compatível com `800 - 15 - 15`.

🟡 O motor deve calcular dimensões internas a partir da dimensão externa e das espessuras configuradas, não de valores fixos hard-coded.

### RN-002 — Largura interna

Para o caso observado:

```text
largura_interna = largura_total - espessura_lateral_esquerda - espessura_lateral_direita
largura_interna = 800 - 15 - 15 = 770
```

Se houver divisória, recuo, fechamento ou outro componente estrutural, o espaço útil deve ser recalculado por vão.

### RN-003 — Altura por regiões

🟢 O vão selecionado exibe `340` para a região superior e `1880` para a região inferior.

🟡 O cálculo deve considerar bases, divisórias, recuos, folgas e componentes inseridos; a soma visual não deve ser interpretada sem conhecer referências exatas.

### RN-004 — Valores de catálogo

🟢 Pés plásticos aparecem com valor `150`; fechamentos com `50`; vistas com `150`; divisórias/distanciadores com espessuras indicadas.

🟡 Valores devem ser parâmetros de catálogo e não textos decorativos.

### RN-005 — Componentes dependentes

Alterar largura, altura, profundidade ou número de vãos deve recalcular componentes dependentes e invalidar propriedades incompatíveis.

### RN-006 — Seleção de vão

Gavetas, internos, portas e fundos inseridos devem possuir um vão alvo. Sem vão selecionado, o sistema deve desabilitar Inserir ou solicitar seleção.

### RN-007 — Quantidade de gavetas

O valor Número de gavetas deve ser inteiro, positivo, limitado pela altura útil e pelo catálogo. A distribuição deve impedir sobreposição.

### RN-008 — Frentes de gaveta

A frente deve ser compatível com o tipo de caixa e com o espaço livre. Trocar a frente pode alterar dimensões visuais e folgas.

### RN-009 — Divisória com recuo

Com Recuo Frontal e Sem Recuo Frontal são variantes geométricas distintas. Não podem ser apenas nomes diferentes do mesmo objeto.

### RN-010 — Fundo automático

Quando Inserir automaticamente estiver marcado, a inclusão ou alteração estrutural deve recalcular o fundo conforme a opção Inteiro/Inteiro Recuado.

### RN-011 — Porta basculante

Portas classificadas como Basculante devem respeitar eixo, região superior e área de abertura próprios. 🔴 Dimensões e regras exatas não aparecem nas capturas.

### RN-012 — Porta deslizante

Portas deslizantes devem respeitar trilhos, sobreposição, quantidade de folhas, sentido e interferência entre folhas. 🔴 Os campos não estão visíveis.

### RN-013 — Catálogo condicionado

Os catálogos disponíveis podem variar por tipo de armário, vão, orientação e componentes existentes.

### RN-014 — Inserir invertido

Inserir invertido deve alterar a orientação sem alterar indevidamente as propriedades dimensionais, o ID ou o acabamento.

### RN-015 — Aplicação transacional

OK e Aplicar devem executar validação antes de consolidar. Cancelar deve desfazer alterações não aplicadas.

### RN-016 — Estado de alteração

O sistema deve distinguir estado carregado, alterado, aplicado, inválido e confirmado.

### RN-017 — Conflitos

Se um item não couber ou colidir com componente existente, o sistema deve informar a origem do conflito e impedir ou advertir conforme severidade.

### RN-018 — Não destruição silenciosa

Trocar tipo, reduzir dimensões, remover divisórias ou inserir portas/gavetas não deve apagar componentes incompatíveis sem informar o usuário.

---

## 7. Máquina de estados

```text
CARREGANDO
  -> PRONTO_SEM_ALTERAÇÃO
  -> EDITANDO
  -> VALIDANDO
  -> APLICADO
  -> CONFIRMADO

EDITANDO -> INVÁLIDO       se houver componente incompatível ou medida inválida
EDITANDO -> VALIDANDO      ao clicar Aplicar ou OK
VALIDANDO -> EDITANDO      se houver erro ou aviso que exige ação
VALIDANDO -> APLICADO      se a alteração for aceita sem fechar
VALIDANDO -> CONFIRMADO    se OK confirmar
EDITANDO -> CANCELANDO     ao clicar Cancelar
CANCELANDO -> PRONTO       após restaurar estado anterior
QUALQUER -> ERRO           se houver falha de cálculo/catálogo
```

### Estados de seleção

- `NENHUM`
- `VÃO_SELECIONADO`
- `COMPONENTE_SELECIONADO`
- `ITEM_DE_CATÁLOGO_SELECIONADO`
- `INSERÇÃO_EM_PREPARAÇÃO`
- `ALTERAÇÃO_PENDENTE`

### Invariantes

- O desenho deve refletir o modelo atual ou informar processamento.
- Os controles de inserção devem respeitar a seleção do alvo.
- Aplicar/OK não podem confirmar estado estrutural inválido.
- Cancelar deve restaurar o snapshot anterior à edição.
- Qualquer alteração automática deve ser explicável.

---

## 8. Modelo de dados conceitual

```text
Projeto
 └── Ambiente
      └── Armário
           ├── Tipo
           ├── DimensõesGlobais
           ├── Vãos[*]
           │    ├── DimensõesCalculadas
           │    ├── Divisões[*]
           │    ├── Gavetas[*]
           │    ├── Internos[*]
           │    ├── Portas[*]
           │    ├── Deslizantes[*]
           │    └── Fundos[*]
           ├── ComponentesEstruturais[*]
           ├── RegrasDeMovimentação
           ├── Catálogo
           └── EstadoDeEdição
```

### 8.1 Armário

```json
{
  "id": "<id-estavel>",
  "tipo": "Torre p/ Eletros",
  "numeroVaos": 1,
  "dimensoes": {
    "larguraTotal": 800,
    "altura": 2250,
    "profundidade": 550,
    "unidade": "mm"
  },
  "vãos": [],
  "componentes": [],
  "estado": "PRONTO_SEM_ALTERAÇÃO"
}
```

### 8.2 Componente de estrutura

Campos recomendados:

- `id`;
- `tipo`;
- `nomeExibicao`;
- `ativo`;
- `espessura`;
- `dimensoes`;
- `posição`;
- `vãoId`;
- `grupoPaiId`;
- `valorParametros`;
- `origemCatalogo`;
- `selecionável`;
- `visível`.

### 8.3 Item de catálogo

Campos recomendados:

- `catalogoId`;
- `família`;
- `subcategoria`;
- `nome`;
- `descrição`;
- `miniatura`;
- `orientaçãoPermitida`;
- `inserçãoInvertidaPermitida`;
- `restrições`;
- `parâmetros`;
- `compatibilidades`.

### 8.4 Histórico

Cada ação deve guardar:

- tipo da ação;
- alvo;
- estado anterior;
- estado posterior;
- catálogo/versão;
- usuário;
- timestamp;
- se foi manual ou automática.

---

## 9. Catálogo funcional confirmado

### 9.1 Estrutura

| Grupo | Itens confirmados | Parâmetros visíveis |
|---|---|---|
| Laterais | Esquerda, Direita | 15mm |
| Divisão | Divisória | — |
| Bases | Inferior, Superior | 15mm |
| Base especial | Superior Recuada | 15mm |
| Apoio | Pés Plásticos | posições 01–04, 150 |
| Acabamento inferior | Rodapés | frontal, esquerdo, direito |
| Rodapé especial | Rodapés Granito | — |
| Fechamento | Fechamentos | 50 |
| Vistas | Frontal, Esquerda, Direita | 150 |
| Vistas altas | Esquerda, Direita, Frontal | — |

### 9.2 Divisões

| Grupo | Itens |
|---|---|
| Orientação | Vertical, Horizontal, Inserção múltipla |
| Tipo | Divisórias Móveis, Divisórias Fixas, Distanciador, Sem Divisória |
| Recuo | Com Recuo Frontal, Sem Recuo Frontal |
| Divisórias | Interna s/ Recuo — Tras 15mm; Interna c/ Recuo — Tras 15mm |
| Distanciadores | 15mm; Duplo 30mm; p/ Divisão 15mm |

### 9.3 Gavetas

| Grupo | Itens/valores |
|---|---|
| Opções de gavetas | Gaveta c/ CF — Caixa Gaveta c/ Folha / Contra Frente |
| Opções de frentes | Reta — Frente Reta |
| Inserção | Número de gavetas = 4 na captura |
| Subabas | Gavetas, Gaveteiros, Internas, Blum |

### 9.4 Internos/eletros

| Família | Itens confirmados |
|---|---|
| Painéis externos | Painel Forno/Micro Externo; Painel Forno Externo; Painel Micro Externo; Painel Cafeteira Externo |
| Complementos | Frontal Externo; Respiro |
| Eletros | Forno; Microondas; Cafeteira |
| Filtros | Externos; Embutidos |
| Subabas | Painel p/ Eletros; Biblioteca; Apoios; Pistões |

### 9.5 Portas

| Filtro | Valores |
|---|---|
| Posição/tipo | Inferior, Superior, Alta, Basculante |
| Escopo | Ambas, Inteira, Esquerda, Direita |
| Estilos | Reta, Lisa, Almofada, Fresada, Fresada 02, Colonial, Colonial 02, Colonial 03, Bicolor, Gola Horizontal, Gola Vertical, Gola Vertical 2L |

### 9.6 Deslizantes

| Família | Estilos confirmados |
|---|---|
| Material | Alumínio, Madeira |
| Madeira | Lisa, Reta, Almofada, Fresada, Colonial, Bicolor, Gola Vertical, Gola Vertical 2L, Borda Alumínio, Cava Vertical, Chanfrada, Country, Perfil Y Vertical, Perfil Y Vertical 2L |
| Puxadores integrados | Obispa, Contatto, Torralba, Altero |

### 9.7 Fundos

| Grupo | Itens/estado |
|---|---|
| Tipo | Inteiro, Inteiro Recuado |
| Item | Fundo Inteiro 15mm |
| Automação | Inserir automaticamente marcado |
| Inversão | Inserir invertido desabilitado na captura |

---

## 10. Requisitos não funcionais

### RNF-001 — Consistência geométrica

A vista, as cotas e os dados devem representar a mesma configuração.

### RNF-002 — Precisão

Medidas devem preservar precisão suficiente para projeto e fabricação; arredondamentos devem ser explícitos.

### RNF-003 — Desempenho

Inserções e alterações comuns devem atualizar o desenho em tempo interativo. 🔴 O limite de tempo precisa ser definido por complexidade.

### RNF-004 — Usabilidade

A organização por abas, subabas, árvores e miniaturas deve permitir localizar categorias sem depender de memória visual externa.

### RNF-005 — Acessibilidade

Checkboxes, campos, abas, miniaturas e mensagens devem possuir nomes acessíveis e estados anunciáveis.

### RNF-006 — Undo/redo

Toda operação que altere o modelo deve ser reversível.

### RNF-007 — Integridade

Aplicar e OK devem ser transacionais; falhas não podem produzir modelo parcial.

### RNF-008 — Diagnóstico

Falhas devem identificar campo, componente, vão, regra e ação corretiva.

### RNF-009 — Versionamento de catálogo

A configuração deve preservar a versão do catálogo que gerou componentes e cálculos.

### RNF-010 — Compatibilidade

A solução deve manter a distinção entre estrutura, divisões, gavetas, internos, portas, deslizantes e fundos.

---

## 11. Critérios de aceite

### CA-01 — Carregamento

Ao abrir um armário do tipo Torre p/ Eletros, o sistema deve exibir tipo, vãos, largura, altura, profundidade, desenho e componentes ativos.

### CA-02 — Medidas do caso observado

Com largura `800`, altura `2250`, profundidade `550` e laterais de `15mm`, o sistema deve apresentar largura interna de `770`, salvo componente que altere a referência.

### CA-03 — Estrutura

Marcar/desmarcar Base Superior Recuada deve atualizar o modelo e sua representação, sem alterar lateral ou base não relacionada.

### CA-04 — Pés

Ativar Pés Plásticos deve permitir configurar posições 01–04 e seus valores, inicialmente `150` na evidência.

### CA-05 — Rodapés

Selecionar Frontal, Esquerdo ou Direito deve afetar somente a face correspondente.

### CA-06 — Divisão vertical

Escolher uma divisão vertical e inserir deve criar uma separação no vão alvo, atualizar a largura dos subespaços e permitir desfazer.

### CA-07 — Divisão com recuo

A opção com recuo deve produzir geometria diferente da opção sem recuo.

### CA-08 — Distanciador

Inserir Distanciador Duplo 30mm deve reservar espaço compatível com 30mm e não ser tratado como Distanciador 15mm.

### CA-09 — Gavetas

Com o vão superior selecionado e Número de gavetas igual a 4, inserir deve criar quatro unidades distribuídas sem sobreposição e com frente compatível.

### CA-10 — Seleção de vão

A seleção do vão deve ser visível no desenho e refletida na barra inferior como `Selecionado: Vão`.

### CA-11 — Interno

Inserir um item de Painel p/ Eletros deve criar o componente no vão correto e validar suas dimensões.

### CA-12 — Portas

Filtrar Superior, Alta, Basculante ou lado deve alterar o conjunto de opções exibidas.

### CA-13 — Estilo

Inserir um estilo de porta deve atualizar aparência, nomenclatura e representação de abertura.

### CA-14 — Deslizante

Escolher Madeira → Gola Vertical 2L deve preservar família Madeira e estilo escolhido, sem converter para porta comum.

### CA-15 — Fundo automático

Com Inserir automaticamente marcado, a criação/alteração estrutural deve recalcular o Fundo Inteiro 15mm quando aplicável.

### CA-16 — Aplicar

Aplicar deve validar e manter a janela aberta; se não houver alteração, deve permanecer desabilitado ou sem efeito explícito.

### CA-17 — OK

OK deve validar e confirmar as alterações, fechando a janela somente após persistência bem-sucedida.

### CA-18 — Cancelar

Cancelar deve restaurar o último estado confirmado sem apagar o armário anterior.

### CA-19 — Catálogo incompatível

Uma opção incompatível com o vão ou tipo deve ser desabilitada ou gerar erro explicativo, nunca ser inserida silenciosamente.

### CA-20 — Undo/redo

Inserir uma gaveta, desfazer, refazer e inserir uma porta devem manter desenho, árvore e seleção sincronizados.

### CA-21 — Estado sem propriedade

Quando não houver propriedades adicionais, o painel deve informar `Não há propriedades disponíveis!` em vez de exibir campos vazios ambíguos.

### CA-22 — Redimensionamento

Alterar largura/altura/profundidade deve recalcular cotas internas, vãos, divisões, gavetas, portas, fundos e itens internos afetados.

### CA-23 — Perda de dados

Trocar de aba, cancelar ou fechar com alterações pendentes deve preservar o modelo até decisão explícita.

### CA-24 — Colisão e sobreposição

O sistema deve detectar componentes que não caibam ou se sobreponham, informar a causa e impedir confirmação quando o conflito for bloqueante.

---

## 12. Cenários de erro e exceção

| Cenário | Comportamento requerido |
|---|---|
| Largura menor que a soma das laterais | Bloquear, destacar campo e mostrar limite calculado |
| Altura insuficiente para número de gavetas | Bloquear ou reduzir quantidade somente mediante ação explícita |
| Porta incompatível com vão | Desabilitar opção ou apresentar erro explicativo |
| Deslizante sem espaço para trilho | Impedir inserção e informar requisito |
| Fundo automático incompatível | Manter estado anterior e informar conflito |
| Vão não selecionado | Solicitar seleção ou desabilitar Inserir |
| Falha de catálogo | Manter edição local e identificar item indisponível |
| Falha de cálculo | Não confirmar estado como válido |
| Cancelar com alteração | Perguntar/usar política explícita de descarte |
| Aplicar com erro | Não fechar e destacar erros |
| Alteração de tipo | Revalidar todos os componentes dependentes |
| Remoção de componente pai | Informar impacto em filhos e dependências |

---

## 13. Lacunas restantes

1. 🔴 A sequência exata das ações no vídeo ainda precisa ser transcrita por timestamp.
2. 🔴 A unidade dimensional não está escrita nas capturas; `mm` é inferido pelos rótulos.
3. 🔴 Não foi possível confirmar o significado exato de Cota anterior, inferior, posterior e superior.
4. 🔴 Não está confirmado se cada checkbox de componente adiciona, remove, oculta ou apenas seleciona o item.
5. 🔴 Não estão visíveis mensagens de validação, erro ou colisão.
6. 🔴 Não estão visíveis propriedades editáveis após seleção de cada catálogo.
7. 🔴 Não está confirmado o efeito do botão Aplicar em relação ao OK.
8. 🔴 Não está confirmado se o sistema salva automaticamente no projeto.
9. 🔴 Não estão confirmados limites mínimos/máximos dos campos.
10. 🔴 Não estão confirmadas regras de distribuição das gavetas.
11. 🔴 Não estão confirmadas regras de portas basculantes e deslizantes.
12. 🔴 Não estão confirmadas regras de recuo, fechamento, vistas e rodapés.
13. 🔴 Não estão confirmados atalhos de teclado.
14. 🔴 Não estão confirmados formatos de persistência/exportação.
15. 🔴 Não está confirmado se o painel inferior sempre exibe propriedades ou somente após seleção de um item específico.

---

## 14. Matriz de rastreabilidade

| Objetivo | Requisitos | Evidência/aceite |
|---|---|---|
| Configurar estrutura | RF-001 a RF-009, RN-001 a RN-006 | Capturas de estrutura; CA-01 a CA-05 |
| Configurar divisões | RF-010 a RF-015 | Capturas de divisões; CA-06 a CA-08 |
| Configurar gavetas | RF-016 a RF-018 | Captura de gavetas; CA-09 e CA-10 |
| Inserir eletros | RF-019 e RF-020 | Captura de internos; CA-11 |
| Configurar portas | RF-021 a RF-024 | Captura de portas; CA-12 e CA-13 |
| Configurar deslizantes | RF-025 a RF-027 | Captura de deslizantes; CA-14 |
| Configurar fundos | RF-028 e RF-029 | Captura de fundos; CA-15 |
| Confirmar edição | RF-030 a RF-036, RN-015 a RN-018 | CA-16 a CA-24 |

---

## 15. Recomendação de arquitetura

### Camada de domínio

- `Armario`
- `TipoArmario`
- `Vao`
- `ComponenteEstrutural`
- `Divisao`
- `Gaveta`
- `Interno`
- `Porta`
- `Deslizante`
- `Fundo`
- `RegraCatalogo`
- `ValidadorGeometrico`

### Camada de aplicação

- `CarregarArmario`
- `AlterarDimensoes`
- `AlterarNumeroDeVaos`
- `SelecionarVao`
- `InserirComponente`
- `RemoverComponente`
- `AplicarAlteracoes`
- `ConfirmarEdicao`
- `CancelarEdicao`
- `Desfazer`
- `Refazer`

### Camada de apresentação

- shell da janela Construtor de Armários;
- barra de ferramentas;
- viewport frontal;
- painel de abas;
- árvore de componentes;
- catálogo de miniaturas;
- editor de propriedades;
- painel de movimentação;
- barra de estado;
- diálogos e mensagens.

### Princípios

1. O catálogo não deve conter regra geométrica espalhada na UI.
2. O desenho deve consumir o mesmo modelo validado que será persistido.
3. A inserção deve ser comando reversível.
4. A seleção de vão deve ser uma referência de domínio, não apenas coordenada de tela.
5. Os cálculos devem ter testes com os valores confirmados `800`, `2250`, `550`, `770`, `340`, `1880` e `15`.

---

## 16. Definição de pronto

A reanálise estará pronta para implementação quando:

- os 36 requisitos funcionais forem implementados ou explicitamente descartados;
- os catálogos confirmados estiverem cadastrados;
- o caso Torre p/ Eletros reproduzir as medidas observadas;
- cada aba operar sobre o vão correto;
- inserções, alterações e cancelamentos forem reversíveis;
- validações impedirem configurações geometricamente inválidas;
- todos os itens marcados 🔴 forem resolvidos por vídeo, teste ou decisão de negócio;
- a sequência temporal do vídeo for anexada à matriz de rastreabilidade;
- a especificação puder ser entregue a uma equipe sem necessidade de consultar as capturas para entender o comportamento.

**Conclusão:** esta versão substitui a elicitação genérica anterior por uma especificação baseada em evidências visuais diretas do Construtor de Armários. Ela confirma uma arquitetura de edição paramétrica por vãos, com catálogos especializados para estrutura, divisões, gavetas, internos/eletros, portas, deslizantes e fundos; também explicita os cálculos, estados, dependências, validações e lacunas que ainda precisam ser confirmados no vídeo.
