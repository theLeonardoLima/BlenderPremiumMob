# Editor de Armário

Guia rápido para editar um módulo inteiro numa tela própria, com visão de conjunto, rascunho e confirmação. O fluxo é
o do **Construtor de Armários** do Promob: **escolher o vão na vista → aba → item → Inserir → Aplicar ou OK**. Vale
para os módulos frameless, face frame, closets e os paramétricos do CAFFMob Draw.

## 1. Abrir

Selecione o módulo (ou qualquer peça ou frente dele) e clique em **Abrir editor de armário**. O botão fica em três
lugares:
- na caixa **Medidas e cotas** da seção **Selecionado**;
- no menu do botão direito;
- no HUD da viewport.

Sem um módulo selecionado, o botão fica indisponível com o aviso **Selecione um módulo**.

O editor abre numa janela nova:
- **à esquerda**, a vista frontal do módulo: estrutura, vãos, prateleiras, divisórias e frentes, com as medidas. No
  rodapé da vista, uma barra mostra o que está selecionado: **Selecionado: Vão 1 › de cima**, uma peça ou **(nenhum)**;
- **à direita**, o painel do editor. No topo ficam:
  - o tipo e a biblioteca (por exemplo, **Tipo: Balcão · Frameless**);
  - o estado do rascunho (**Sem alterações**, **Rascunho alterado** ou **Aplicado**);
  - as sete abas, só com ícone (o nome aparece ao passar o mouse);
  - o nome da aba ativa.

O editor sempre abre em **Estrutura**. A roda do mouse aproxima e afasta a vista.

### Escolher o vão

Clique num vão da vista: ele fica em vermelho translúcido e é nele que as abas inserem. Clicar numa divisória a
seleciona (para mover com as setas, veja a seção 2). Um armário sem divisões tem um vão só, que já vem escolhido.

Nas abas que inserem algo, o bloco do topo diz onde a inserção vai acontecer: **Vão: Vão 1 › de cima**. Sem vão
escolhido, ele mostra **Clique num vão na vista**, e o botão **Inserir** fica apagado com o motivo **Selecione um vão
na vista**.

## 2. Aba Estrutura

- **Definições:**
  - **Número de vãos:** divide o vão interno em partes iguais, com divisórias verticais. Exemplo: um armário de
    800 mm com laterais de 15 mm tem 770 mm de vão; com 3 vãos e divisórias de 15 mm, cada vão fica com
    (770 − 2 × 15) / 3 = 246,7 mm.
  - **Largura total, Altura, Profundidade:** a faixa permitida aparece embaixo de cada uma. Um valor fora da faixa não
    é aplicado: o campo fica vermelho e aparece a mensagem **DIM-003** com a faixa.
- **Componentes:** uma linha para cada chapa da caixa (tampo, base, fundo, lateral esquerda, lateral direita). A
  caixa de marcar liga e desliga a chapa.
  - **✎ Editar** muda a espessura e o material só neste armário.
  - Desmarcar remove a chapa no modo escolhido ao lado:
    - **Manter tudo** (padrão): só a chapa sai;
    - **Estender as vizinhas:** as vizinhas avançam até a borda;
    - **Reduzir o armário:** as medidas externas diminuem pela espessura.
- **Componentes extras** (árvore, com o valor ao lado):
  - **Base Superior Recuada**: troca o tampo;
  - **Pés Plásticos**: 150 mm, com as posições 01 a 04;
  - **Rodapés**: frontal, esquerdo e direito;
  - **Rodapés Granito**;
  - **Fechamentos**: 50 mm;
  - **Vistas** e **Vistas (alto)**: esquerda, direita e frontal, de 150 mm.

  Os pés entram na lista de ferragens; os demais extras entram no plano de corte.
- **Posição:** as quatro cotas da divisória selecionada (frente, baixo, trás, cima). Digitar uma cota move a
  divisória. Sem divisória selecionada, elas ficam apagadas.
- **Movimentação:** **Passo** (padrão 10 mm) e **Passo inicial**. Com uma divisória selecionada, as **setas do
  teclado** a movem pelo passo.
- **Materiais:** material de um grupo de peças e das frentes do vão.

O que cada biblioteca permite remover:

| Biblioteca | Remover / editar | Estender as vizinhas | Reduzir o armário |
|---|---|---|---|
| Módulo paramétrico | todas as chapas | todas as chapas | todas as chapas |
| Frameless | todas as chapas | só a base | — |
| Closets | laterais, base e tampo | — | — |
| Face frame | todas as chapas | — | — |

## 3. Aba Divisões

1. Confira a chapa usada: o material e a espessura do componente **Divisória** do Configurador de Dimensões, na
   linha do módulo.
2. Escolha o modo:
   - **Vertical**: separa esquerda e direita;
   - **Horizontal**: separa cima e baixo;
   - **Inserção múltipla**: várias chapas iguais de uma vez, na orientação e na **Quantidade** escolhidas.
3. Escolha o tipo:
   - **Divisórias Móveis**: reguláveis. As peças vizinhas recebem a furação para pino de prateleira, a 37 mm da
     frente e de trás, com passo de 32 mm. A furação sai no JSON de produção.
   - **Divisórias Fixas**: a chapa comum.
   - **Distanciador**: ocupa uma faixa ao lado sem dividir o vão. As opções são **15 mm**, **Duplo 30 mm** e **p/
     Divisão 15 mm**, que acompanha a divisória.
   - **Sem Divisória**: tira a divisória que criou o vão escolhido e junta os dois lados.
4. No catálogo, escolha **Interna s/ Recuo** ou **Interna c/ Recuo**, ou marque os recuos na mão.
5. Clique em **Inserir em <vão>**.

A lista **Divisões** mostra cada chapa, com **✎ Editar** e **✕ Remover**. O painel recolhido **Interior da
biblioteca** faz as divisões internas da própria biblioteca (prateleiras por quantidade).

Mensagens desta aba:
- **DIV-001**: um lado com menos de 50 mm;
- **DIV-002**: recuos que deixam a chapa com menos de 50 mm de profundidade;
- **DIV-003**: o vão da divisão não existe mais.

As três impedem Aplicar e OK.

## 4. Aba Gavetas

As gavetas entram no **vão da biblioteca** que contém o vão escolhido. Ele aparece contornado em verde na vista e no
bloco do topo, como **Vão da biblioteca: bay0/opening0**. Um vão fora de um vão da biblioteca deixa o Inserir apagado
com o motivo.

- **Gavetas**: gaveta com contra-frente.
- **Gavetões**: frente alta, de 2 a 4 por vão.
- **Internas**: gaveta atrás da porta, sem puxador. Só existe no frameless.
- **Blum**: gaveta com corrediça Blum, contada à parte na lista de ferragens.

Escolha também o estilo da frente (da biblioteca do módulo), o **Puxador** e o **Número de gavetas**. Cada gaveta conta
um par de corrediças na lista de ferragens. O módulo paramétrico não tem gavetas: a aba avisa.

## 5. Aba Internos

- **Painel p/ Eletros:** painéis com recorte para forno, micro-ondas e cafeteira, filtrados em **Externos** ou
  **Embutidos**. Inclui também o **Frontal**, os eletros de referência (que ficam fora do plano de corte) e o
  **Respiro**. O recorte do painel sai no JSON como usinagem.
- **Biblioteca:** os módulos salvos ficam em **Inserir › Meus módulos**.
- **Apoios:** prateleira de apoio de eletro.
- **Pistões:** pistão para porta basculante (ferragem).

Um item que não cabe no vão aparece apagado, com a medida mínima na dica. A lista **Inseridos** mostra o que já entrou,
com **✕** para remover.

## 6. Aba Portas

- **Região:** Inferior, Superior, Alta ou **Basculante**.
- **Portas:** **Ambas** (duas folhas), **Inteira**, **Esquerda** ou **Direita**.
- **Estilo** e **Puxador** vêm da biblioteca do módulo.
- **Inserir invertido** troca o lado da dobradiça. As linhas de abertura aparecem tracejadas na vista.

A porta entra no vão da biblioteca que contém o vão escolhido, como as gavetas.

## 7. Aba Deslizantes

- **Família:** **Madeira** (Lisa, Reta, Almofada, Gola Vertical, Cava Vertical, Perfil Y e os de puxador integrado:
  Obispa, Contatto, Torralba, Altero) ou **Alumínio** (Quadro Alumínio).
- **Folhas:** 2 ou 3. **Inserir invertido** troca a ordem das folhas.

Os trilhos entram na lista de ferragens. As folhas correm até a lateral ou até a divisória do armário e fecham até o
montante da outra folha. Se algo atravessa o caminho, a mensagem diz **não corre: esbarra em <peça>**. Sem
profundidade para os trilhos, a aba avisa a medida necessária. **Remover deslizantes** tira o conjunto.

## 8. Aba Fundos

- **Inteiro:** o fundo da biblioteca.
- **Inteiro Recuado:** o fundo anda para dentro pela medida do **Recuo** (padrão 20 mm), e o vão perde essa
  profundidade.
- **Inserir automaticamente** (marcado por padrão): quando o armário muda de medida ou a biblioteca reconstrói as
  peças, o recuo é reaplicado. Um fundo que você removeu continua removido.
- **Inserir** aplica o modo e devolve o fundo, se ele tiver sido removido.

Um armário sem fundo (o roupeiro padrão, por exemplo) recebe o aviso **Este armário não tem fundo**.

## 9. Rodapé: mensagens, desfazer e confirmar

O rodapé é o mesmo em todas as abas.

- **Mensagens:** o resumo com a contagem e, aberta, a lista com código, componente, valor, faixa e o que fazer. Os
  códigos são:
  - **DIM**: medida;
  - **GEO-001**: componente fora do módulo;
  - **GEO-002**: peças que entram umas nas outras (inclusive uma divisória nossa cruzando uma prateleira da
    biblioteca);
  - **DIV**: divisão;
  - **STR**: estrutura;
  - **LIB**: aviso da biblioteca.

  Só erro impede Aplicar e OK.
- **Desfazer** e **Refazer** (ou **Ctrl+Z** e **Ctrl+Shift+Z**) andam no rascunho do editor sem mexer no desfazer da
  cena.
- **OK** grava tudo e fecha.
- **Cancelar** volta ao último Aplicar (ou ao estado de quando o editor abriu) e fecha. Com alterações, pede
  confirmação.
- **Aplicar** grava sem fechar o editor. Cada Aplicar é um passo de desfazer na cena e passa a ser a referência do
  Cancelar. Sem mudança, ou com erro, o botão fica apagado com o motivo.
- **Fechar** (ou **Esc**), com alterações pendentes, pergunta: **Continuar editando**, **Descartar** ou **Confirmar** (o mesmo que OK).
- **Salvar como módulo** grava o armário, como está no editor, na biblioteca do usuário.

Se você fechar a janela do editor pelo sistema, as alterações não aplicadas são descartadas, e a barra de status
avisa **Editor fechado: alterações descartadas**.

## 10. Produção

- **Plano de corte:** as chapas extras, as divisórias, os distanciadores, os painéis de eletro e as folhas de
  correr entram com o componente certo. Ferragens e eletros de referência ficam de fora.
- **Ferragens:** na seção **Produção › Plano de corte**, a caixa **Ferragens** mostra o nome, a quantidade e o módulo
  de cada ferragem: pés, corrediças (Blum à parte), pistões e trilhos.
- **JSON de produção 2.2.0:**
  - a lista `hardware`;
  - a furação das divisórias móveis em `parts[].drilling`;
  - os recortes de eletro em `machining`.

  Leitores da versão 2.1 continuam lendo o arquivo.

> **Face frame:** estrutura, divisões e extras aparecem no 3D, mas os módulos face frame ainda não entram no plano de
> corte nem na lista de ferragens.
