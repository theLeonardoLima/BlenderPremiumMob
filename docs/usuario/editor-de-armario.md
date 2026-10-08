# Editor de Armário

Guia rápido para editar um módulo inteiro numa tela própria, com visão de conjunto, rascunho e confirmação. Vale para
os módulos frameless, face frame, closets e os paramétricos do CAFFMob Draw.

## 1. Abrir

Selecione o módulo (ou qualquer peça ou frente dele) e clique em **Abrir editor de armário**. O botão fica na caixa
**Medidas e cotas** da seção **Selecionado**, no menu do botão direito e no HUD da viewport. Sem um módulo selecionado, o botão fica
indisponível com o aviso **Selecione um módulo**.

O editor abre numa janela nova:
- **à esquerda**, a vista frontal do módulo: estrutura, vãos tracejados, prateleiras, divisórias e frentes, com as
  medidas;
- **à direita**, a aba **Editor de Armário** com os painéis.

Clicar num componente na vista o seleciona na lista **Componentes**, e o contrário também vale. A roda do mouse
aproxima e afasta.

## 2. Editar

- **Medidas:** largura, altura e profundidade, com a faixa permitida embaixo de cada uma. Um valor fora da faixa não é
  aplicado: o campo fica vermelho e aparece a mensagem **DIM-003** com a faixa.
- **Personalizar:** as edições de **Selecionado** › **Personalizar** (frente do vão, estilo, puxador, material e divisões
  internas), aplicadas ao vão do componente selecionado. Uma seção que a biblioteca do módulo não tem aparece
  desabilitada, com o motivo.
- **Mensagens:** erros e avisos, com o código, o componente, o valor, a faixa e o que fazer. Os códigos são:
  - **DIM**: medida;
  - **GEO-001**: componente fora do módulo;
  - **GEO-002**: divisões que entram umas nas outras;
  - **LIB**: aviso da biblioteca.
  Só erro impede Confirmar.
- **Ajustes automáticos:** o que o recálculo mudou sozinho depois das suas edições, como frentes redistribuídas ou
  peças que entraram ou saíram.

Cada edição aparece na hora no módulo e na vista frontal. **Ctrl+Z** e **Ctrl+Shift+Z**, ou os botões **Desfazer** e
**Refazer**, andam no rascunho do editor sem mexer no desfazer da cena.

## 3. Confirmar, cancelar ou fechar

- **Confirmar** aplica tudo como um único passo de desfazer: depois, um **Ctrl+Z** na cena devolve o módulo como era
  antes de abrir o editor. Com erro na lista, o botão fica indisponível.
- **Cancelar** devolve o módulo exatamente como estava ao abrir o editor. Com alterações, o editor pede confirmação
  antes.
- **Fechar** (ou **Esc**), com alterações pendentes, pergunta: **Continuar editando**, **Descartar** ou **Confirmar**.
- Se você fechar a janela do editor pelo sistema, as alterações são descartadas e a barra de status avisa **Editor
  fechado: alterações descartadas**.
- **Salvar como módulo** grava o armário, como está no editor, na biblioteca do usuário.
