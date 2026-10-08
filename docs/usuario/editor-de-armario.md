# Editor de Armário

Guia rápido para editar um módulo inteiro numa tela própria, com visão de conjunto, rascunho e confirmação. Vale para
os módulos frameless, face frame, closets e os paramétricos do CAFFMob Draw.

## 1. Abrir

Selecione o módulo (ou qualquer peça ou frente dele) e clique em **Abrir editor de armário**. O botão fica em três
lugares:
- na caixa **Medidas e cotas** da seção **Selecionado**;
- no menu do botão direito;
- no HUD da viewport.

Sem um módulo selecionado, o botão fica indisponível com o aviso **Selecione um módulo**.

O editor abre numa janela nova:
- **à esquerda**, a vista frontal do módulo: estrutura, vãos tracejados, prateleiras, divisórias e frentes, com as
  medidas;
- **à direita**, a aba **Editor de Armário**. No topo ficam o nome do módulo, a biblioteca, o estado do rascunho e
  três abas: **Estrutura**, **Divisão** e **Acabamento**. O editor sempre abre em **Estrutura**.

A roda do mouse aproxima e afasta a vista.

## 2. Aba Estrutura

- **Medidas:** largura, altura e profundidade, com a faixa permitida embaixo de cada uma. Um valor fora da faixa não é
  aplicado: o campo fica vermelho e aparece a mensagem **DIM-003** com a faixa.
- **Componentes externos:** uma linha para cada chapa da caixa que o módulo tem (tampo, base, fundo, lateral esquerda,
  lateral direita), com as medidas, o material da chapa e a espessura.
  - **✎ Editar:** muda a espessura e o material da chapa (MDF, MDP…) só neste armário. **0** e **Do Configurador**
    voltam aos valores do Configurador de Dimensões. A linha passa a mostrar **alterado**.
  - **✕ Remover:** abre uma janela com três modos:
    - **Manter tudo** (padrão): só a chapa sai. Medidas, demais chapas e vão interno ficam como estão.
    - **Estender as vizinhas:** as chapas vizinhas avançam até a borda e o vão interno cresce.
    - **Reduzir o armário:** as medidas externas diminuem pela espessura da chapa e o vão interno fica igual.

    A chapa removida some da vista e do plano de corte. Na lista ela aparece como **removido** e ganha o botão
    **Restaurar**, que a devolve e desfaz o ajuste de medidas do modo usado.

O que cada biblioteca permite:

| Biblioteca | Remover / editar | Estender as vizinhas | Reduzir o armário |
|---|---|---|---|
| Módulo paramétrico | todas as chapas | todas as chapas | todas as chapas |
| Frameless | todas as chapas | só a base | — |
| Closets | laterais, base e tampo | — | — |
| Face frame | todas as chapas | — | — |

Os modos indisponíveis aparecem apagados na janela, com o motivo.

## 3. Aba Divisão

Acrescenta chapas de divisão que ocupam um vão inteiro: a **vertical** separa esquerda e direita; a **horizontal**
separa cima e baixo.

1. Confira no topo a chapa que será usada: o material e a espessura do componente **Divisória** do Configurador de
   Dimensões, na linha do módulo (por exemplo, "Chapa: MDP 15 mm (Configurador › DOR)").
2. Escolha o **Vão** na lista ou clique nele na vista. O vão escolhido fica destacado, com o nome escrito, por exemplo
   "Vão 1 › esquerdo". Um armário sem divisões tem um vão só, que já vem escolhido.
3. Escolha **Vertical** ou **Horizontal**.
4. Marque **Recuo na frente** e/ou **Recuo atrás**, se quiser. Cada um tem a sua medida (padrão 20 mm) e só reduz a
   profundidade da chapa.
5. Clique em **Adicionar em <vão>**. A chapa entra no meio do vão e o divide em dois.

A lista **Divisões** mostra cada chapa:
- **✎ Editar:** muda a posição (distância da face esquerda ou de baixo do vão), os recuos, o material e a espessura.
- **✕ Remover:** tira a chapa. As divisões que estavam dentro dos vãos dela saem junto.

Mensagens desta aba:
- **DIV-001**: um dos lados ficou com menos de 50 mm. A mensagem mostra a faixa de posição permitida.
- **DIV-002**: os recuos deixaram a chapa com menos de 50 mm de profundidade.
- **DIV-003**: o vão da divisão não existe mais.

As três impedem Confirmar.

Quando o armário muda de medida, mesmo fora do editor, as divisões acompanham o vão: a posição fica igual a partir da
face esquerda ou de baixo, e o resto se ajusta.

> **Face frame:** remoções e divisões aparecem no 3D, mas os módulos face frame ainda não entram no plano de corte. O
> aviso aparece nas duas abas.

## 4. Aba Acabamento

- **Componentes:** a lista das peças do módulo. Clicar num componente na vista o seleciona na lista, e o contrário
  também vale.
- **Personalizar:** frente do vão, estilo, puxador, material e divisões internas da biblioteca, aplicados ao vão do
  componente selecionado. Uma seção que a biblioteca não tem aparece desabilitada, com o motivo.

## 5. Rodapé: mensagens, desfazer e confirmar

O rodapé é o mesmo nas três abas.

- **Mensagens:** erros e avisos, com o código, o componente, o valor, a faixa e o que fazer. Os códigos são:
  - **DIM**: medida;
  - **GEO-001**: componente fora do módulo;
  - **GEO-002**: divisões que entram umas nas outras;
  - **DIV**: divisão;
  - **STR**: espessura fora da faixa ou modo de remoção indisponível;
  - **LIB**: aviso da biblioteca.

  Só erro impede Confirmar.
- **Ajustes automáticos:** o que o recálculo mudou sozinho depois das suas edições.
- **Desfazer** e **Refazer** (ou **Ctrl+Z** e **Ctrl+Shift+Z**) andam no rascunho do editor sem mexer no desfazer da
  cena.
- **Confirmar** aplica tudo como um único passo de desfazer: depois, um **Ctrl+Z** na cena devolve o módulo como era
  antes de abrir o editor. Com erro na lista, o botão fica indisponível.
- **Cancelar** devolve o módulo exatamente como estava ao abrir o editor, inclusive chapas removidas e divisões. Com
  alterações, o editor pede confirmação antes.
- **Fechar** (ou **Esc**), com alterações pendentes, pergunta: **Continuar editando**, **Descartar** ou **Confirmar**.
- Se você fechar a janela do editor pelo sistema, as alterações são descartadas e a barra de status avisa **Editor
  fechado: alterações descartadas**.
- **Salvar como módulo** grava o armário, como está no editor e com estrutura e divisões, na biblioteca do usuário.
