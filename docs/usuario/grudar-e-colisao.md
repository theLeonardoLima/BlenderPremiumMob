# Grudar em superfícies e colisões

Guia rápido para prender um item numa parede, num painel ou em outra face plana e para conferir se há itens ocupando o
mesmo espaço. Tudo fica na barra lateral da Viewport 3D (tecla **N**), aba **CAFFMob Draw**.

## 1. Elemento filho: o que é

Um item grudado é **elemento filho** da superfície onde está (o hospedeiro). A seção **Selecionado** › **Posição e vínculo**
mostra, por exemplo, **Elemento filho de: Parede 3 — frente**.

O elemento filho:
- vai junto quando o hospedeiro se move ou gira;
- continua encostado na mesma face quando o hospedeiro muda de medida. Por exemplo, se a parede passa de 150 para
  200 mm, o aéreo grudado atrás dela continua encostado;
- anda só no plano da face. Se você o mover com **G**, ao soltar ele volta para a face, no lugar em que foi solto.

Os módulos que já estavam na parede, inclusive em arquivos antigos, viram elementos filhos dela sozinhos ao abrir o
arquivo. Nada se move.

## 2. Grudar

- **Pelo comando:**
  1. Selecione o item.
  2. Clique em **Grudar** (no painel ou no menu do botão direito).
  3. Clique na face plana onde ele deve ficar.
  O fundo do item encosta na face, centrado no ponto do clique. Numa face deitada (o tampo de um módulo, por exemplo),
  quem encosta é a base do item.
- **Pelo ímã:** solte um módulo ou uma geometria com o fundo perto de uma face plana e ele gruda nela. A distância
  padrão é **50 mm**. Para ligar, desligar ou mudar a distância, vá em **Edit › Preferences › Add-ons › CAFFMob
  Draw**, seção **Grudar em superfície**. Grudar pelo ímã é um passo de desfazer próprio: **Ctrl+Z** solta o item.

Piso e teto não contam como face para grudar. Uma face curva é recusada com o aviso **A face não é plana**.

## 3. Ajustar e soltar

Em **Selecionado** › **Posição e vínculo**:
- **Posição U** e **Posição V** movem o item na face. **Distância** afasta o item da face; um valor negativo faz o
  item entrar no hospedeiro, como num produto embutido. **Giro** gira o item em torno da normal da face.
- **Mover no plano** arrasta o item com o mouse na face. Segure **Ctrl** sobre a face de outro objeto para trocar de
  hospedeiro. **Esc** desfaz o arraste.
- **Desgrudar** solta o item. Ele fica onde está e deixa de acompanhar o hospedeiro.

No hospedeiro, o painel lista os **Elementos filhos** dele.

Avisos na barra de status:
- **Item fora da face: <item>**: o hospedeiro encolheu e o item ficou para fora. Ele continua no lugar e grudado.
- **Vínculo perdido: <item>**: o hospedeiro foi apagado. O item fica no mesmo lugar, solto.

## 4. Colisões

Em **Verificar** › **Colisões**:
- **Verificar colisões** confere a cena toda. **Selecionado** confere só o item selecionado e o que ele toca.
- Encostar (até 1 mm) não é colisão. A lista mostra, nesta ordem: **Penetração em parede** (inclui obstáculos e
  pilares), **Colisão entre itens** e **Piso ou teto**, com a profundidade de cada uma.
- A lupa (**Ir para a colisão**) seleciona os dois itens e enquadra a vista neles.
- **Afastar até encostar** move o item pelo menor caminho até ele só encostar no outro. Um item grudado anda só no
  plano da face.
- Os itens em colisão aparecem contornados na viewport, com o tipo escrito ao lado.

Não contam como colisão:
- as peças do mesmo módulo entre si;
- um agregado e o pai dele;
- um elemento filho e o hospedeiro dele;
- uma porta ou janela de ambiente e a parede dela;
- itens com **Colisão: Desativada** (**Selecionado** › **Colisão**).

Ao soltar um item movido, o CAFFMob Draw confere só ele. Se colidir, avisa **<item> colide com <outro>** e destaca os
dois, sem mover nada.

Quando um item verificado se mexe, o painel avisa **Desatualizado, verifique de novo**. Um resultado desatualizado
nunca aparece como "sem colisões".

Ao salvar, a barra de status mostra quantas colisões estão pendentes, ou avisa que elas não foram verificadas desde a
última mudança. O arquivo é salvo de qualquer forma.

A chave **Evitar Sobreposição** (**Produção/Projeto** › **Configurações**) desliga também a verificação de colisões.

Durante o arraste, a prévia do ímã mostra a face e o contorno de onde o item vai encostar (ver `barra-lateral.md`).
