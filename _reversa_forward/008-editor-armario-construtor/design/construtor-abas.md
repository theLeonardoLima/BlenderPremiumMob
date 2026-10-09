# Design brief: editor de armário no modelo do Construtor (T036, `/impeccable shape`)

> Data: 2026-10-08. Registro: interface de ferramenta (Operate).
> Superfície: barra lateral do editor de armário (Image Editor › região UI, ~300 px), Blender 5.2.
> Evidência: capturas em `inputs/`. Decisões do titular nesta passada: abas **só com ícone + nome da aba ativa**;
> catálogo em **grade de botões grandes**.

## 1. Público e trabalho

Quem usa é o projetista que vem do Promob, com o armário aberto e a vista frontal à esquerda. Ele trabalha no ciclo
**escolher vão na vista → aba → item → Inserir → Aplicar/OK**. Sucesso: reconhecer o fluxo do Construtor sem ler
manual e nunca clicar num Inserir que não faz nada.

## 2. Direção

- **Mundo visual = o tema do Blender.** Só controles nativos do `UILayout`: `prop_tabs_enum` (só ícone), `box`,
  `grid_flow`, botões com `icon_value` das miniaturas, `prop` e `alert`. Nenhuma cor própria na barra; o estado na
  vista frontal (vermelho no vão, verde no vão da biblioteca, tracejado na abertura).
- **Tese:** "o vão manda". Toda aba começa dizendo **em qual vão** vai inserir. Sem vão, a aba explica como escolher,
  e o Inserir fica apagado com o motivo.
- **Momento focal:** o botão **Inserir em <vão>**, largo e no fim do catálogo, sempre no mesmo lugar em todas as abas.

## 3. Estrutura do painel (de cima para baixo)

**Cabeçalho (sempre)**
- Linha 1: tipo e biblioteca ("Tipo: Balcão · Frameless").
- Linha 2: estado do rascunho ("Sem alterações" / "Rascunho alterado" / "Aplicado").
- Linha 3: fileira de 7 abas só com ícone (tooltip com o nome).
- Linha 4: o **nome da aba ativa** em destaque, para não depender do ícone.

**Bloco "Alvo" (abas de inserção)**
- Uma linha: "Vão: Vão 1 › de cima" com ícone de seleção, ou, apagado, "Clique num vão na vista".
- Em Gavetas e Portas, uma segunda linha: "Vão da biblioteca: bay0/opening0", com aviso quando ele é maior que o vão
  escolhido.

**Abas**

| Aba | Conteúdo, na ordem |
|---|---|
| Estrutura | Definições (Número de vãos, Largura total, Altura, Profundidade, com a faixa) · Componentes (árvore: caixas com espessura no nome; extras com o valor ao lado; nós Pés/Rodapés/Vistas/Vistas altas recolhíveis) · Posição (4 cotas, apagadas sem divisória selecionada) · Movimentação (Passo inicial, Passo; recolhido) · Materiais (recolhido) |
| Divisões | Modo (Vertical / Horizontal / Inserção múltipla) · Tipo (Móveis / Fixas / Distanciador / Sem Divisória) · catálogo do tipo em grade (Com/Sem recuo; Distanciadores) · recuos (caixa + medida) · Quantidade (só na múltipla) · Inserir · lista de divisões · Interior da biblioteca (recolhido) |
| Gavetas | Subaba (Gavetas / Gavetões / Internas / Blum) · "Opções de gavetas" (item com miniatura + descrição) · "Opções de frentes" (estilo) · Puxador · Número de gavetas · Inserir |
| Internos | Subaba (Painel p/ Eletros / Biblioteca / Apoios / Pistões) · filtro (Externos / Embutidos) · grade · Inserir · lista do que foi inserido (com remover) |
| Portas | Região (Inferior / Superior / Alta / Basculante) · Portas (Ambas / Inteira / Esquerda / Direita) · Estilo · Puxador · Inserir invertido · Inserir |
| Deslizantes | Família (Madeira / Alumínio) · grade de estilos · Folhas (2 ou 3) · Inserir invertido · Inserir · aviso de profundidade · Remover deslizantes |
| Fundos | Inteiro / Inteiro Recuado · Recuo (só no recuado) · Inserir automaticamente · item "Fundo Inteiro <espessura>" · Inserir |

**Catálogo em grade:**
- `grid_flow` de 2 colunas;
- cada item é um botão alto (`scale_y` 3) com a miniatura (`icon_value`) e o nome;
- o item escolhido fica pressionado (`depress=True`);
- um item que não cabe no vão fica apagado e mostra a medida mínima no tooltip;
- uma lista vazia mostra "Nenhum item nesta categoria".

**Propriedades (área inferior das abas de inserção):** os parâmetros do item escolhido (descrição, medidas). Sem
propriedade, uma linha apagada e centrada: **"Não há propriedades disponíveis"**.

**Rodapé (sempre)**
- Mensagens: resumo com contagem e o ícone de gravidade; a lista abre recolhida.
- Desfazer e Refazer.
- **OK** (maior), Cancelar e **Aplicar**, nessa ordem, como no Construtor. Aplicar fica apagado sem mudança ou com
  erro, com o motivo no tooltip.
- Fechar e Salvar como módulo.

**Vista frontal**
- Barra fixa no rodapé da área: "Selecionado: (nenhum) / Vão 1 › de cima / <peça>".
- O vão alvo em vermelho translúcido.
- O vão da biblioteca contornado em verde (abas Gavetas e Portas).
- Linhas de abertura das portas tracejadas.

## 4. Estados e faixas

- Árvore: 5 componentes + 20 itens de extras; os nós recolhidos por padrão, exceto Componentes.
- Catálogo: de 1 a 18 itens; Deslizantes Madeira é o maior (18).
- Sem vão escolhido: bloco Alvo apagado e Inserir apagado. Com vão, mas sem vão da biblioteca: Gavetas e Portas
  apagadas com o motivo.
- Biblioteca sem a capacidade (por exemplo, gaveta interna fora do frameless): o item fica apagado com o motivo no
  tooltip.

## 5. Restrições

- pt-BR + en-US.
- Estado sempre em texto, além da cor.
- Nada de widget fora do `UILayout`.
- Miniaturas PNG versionadas, com ícone nativo quando faltarem.
