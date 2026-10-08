# Agregados e folhas de porta

Guia rápido para usar modelos 3D de fora no projeto, por exemplo uma porta baixada do SketchUp.
Tudo fica na barra lateral da Viewport 3D (tecla **N**), aba **CAFFMob Draw**: importar fica em **Inserir** › **Importar modelo 3D**; converter e ajustar, em **Selecionado** ›
**Agregados e folhas**.

## 1. Trazer o modelo

Clique em **Importar modelo 3D** e escolha um arquivo **OBJ**, **FBX**, **glTF** ou **GLB**.
O Blender não abre `.skp`. Exporte do SketchUp num desses formatos, ou importe com outro addon: qualquer malha da cena pode ser convertida.

Na janela de arquivo, à direita, há duas opções:
- **Unidade do arquivo:** **Automática** (padrão), mm, cm, m ou pol. A Automática mede o modelo: se uma medida passar
  de 50 unidades, ele está em milímetros. Uma janela de 1400 mm entra com 1,40 m, e não com 1400 m. O aviso no fim
  da importação diz a unidade usada.
- **Eixo vertical:** **Z** (padrão; SketchUp, Promob e a maioria dos CAD) ou **Y**. Se o modelo entrar deitado, importe
  de novo trocando o eixo.

Os nomes das peças e os materiais do arquivo são mantidos.

## 2. Converter em agregado

1. Selecione a malha e, **por último**, o elemento pai (um módulo, uma peça, uma parede ou um painel).
2. Clique em **Converter em agregado**. Ele fica preso à face do pai mais próxima.

Com o agregado selecionado:
- Ao mover, girar ou apagar o pai, o agregado vai junto. Ao apagar o pai, o CAFFMob Draw pergunta se os agregados vão junto.
- **Horizontal** e **Vertical** posicionam o agregado na face. Ele não sai do contorno do pai: um valor acima do limite volta ao máximo, que aparece ao lado do campo.
- **Mover agregado** arrasta com o mouse no plano da face e para na borda. Clique para confirmar; botão direito ou **Esc** volta.
- **Afastamento** positivo afasta do pai. Negativo afunda no pai, no máximo até a espessura dele.
- **Perfurar** recorta o pai onde o agregado afunda, só no 3D. Desligar devolve o pai inteiro.
- **Furo real no plano de corte** leva o recorte para a usinagem da peça pai, no plano de corte e no JSON de produção (`machining`). Ele só funciona quando o pai é uma peça de chapa e o agregado entra pela face da chapa. Sem essa marca, a produção não muda.
- **Peça de produção** põe o agregado na lista de peças, como uma placa com as medidas dele.
- **Desconverter** tira recortes e folha e devolve o objeto como estava.

## 3. Folha de porta

1. Selecione a malha da porta e, por último, o pai (o vão, o módulo ou a parede).
2. Clique em **Converter em folha de porta** e escolha o movimento:
   - **Giro:** o eixo (esquerda, direita, topo ou base), o sentido (para fora ou para dentro) e o **ângulo máximo** (até 180°).
   - **Correr:** o sentido e o **curso**.
3. Arraste a barra **Abertura** (0 a 100%). A folha se move na hora, e a viewport mostra o eixo, o caminho da borda e a posição da folha.

Se a folha encostar numa parede ou em outro objeto ao abrir, ela para no ponto do contato e fica vermelha, com o aviso
**Folha bateu em <objeto>**. A barra trava ali. Fechar é sempre livre e volta à posição original exata.

As folhas convertidas também respondem a **Abrir/Fechar Frentes** e à verificação de interferência. Como as outras
frentes, o projeto é salvo com elas fechadas.

## 4. Grupo de peças

Um modelo de fora costuma vir em muitas peças. Por exemplo, uma folha de janela tem perfis, baguetes, vidro e puxador.
Para mover e abrir tudo junto sem fundir as malhas:
- **Criar grupo:** selecione as peças e clique. Elas viram filhas de um objeto de grupo e se movem juntas. Cada peça
  continua com o nome e o material dela.
- **Desfazer grupo:** devolve as peças soltas. Se o grupo era uma folha ou agregado, ele volta antes à posição
  original.

Um grupo pode ser convertido em agregado ou em folha de porta como uma malha comum. A caixa dele é a soma das peças.

## 5. Janela ou porta pronta: Montar esquadria

1. Importe o modelo e selecione todas as peças.
2. Clique em **Montar esquadria**. O diálogo sugere os grupos pelo nome das peças:
   - as que começam com `Folha_Esquerda`, `Folha_Direita` (ou `Leaf_…`, `Sash_…`) viram folhas;
   - o resto vira a **esquadria** (marco, bordas, trilhos e guias).

   Troque o papel de cada grupo se precisar: Esquadria, Folha de correr, Folha de giro ou Ignorar.
3. Confirme. A esquadria e as folhas são criadas num passo só, e as folhas já ficam prontas para abrir.

### Abrir e fechar com colisão

- A folha de correr abre, por padrão, **para o próprio lado** (a esquerda para a esquerda). O **curso** é a distância
  livre até a esquadria e não aceita valor maior.
- Se sobrar pouco curso nesse lado, o painel avisa **Pouco curso para este lado: inverta o sentido**. Numa janela de
  correr comum, as folhas abrem para o centro, passando uma pela outra: troque o **Sentido**.
- **Abrindo**, a folha para ao encostar na esquadria. O painel e a vista mostram **Folha bateu em <peça>**, e a peça
  fica destacada.
- **Fechando**, a folha para no primeiro destes pontos:
  - a posição original do arquivo;
  - o montante da outra folha, onde ela estiver;
  - a esquadria do outro lado.

  Se parar na outra folha, o aviso é **Folha encostou em <folha>**.

### Instalar na parede

1. Selecione a esquadria e a parede e clique em **Instalar na parede**. Escolha o **peitoril** (padrão 1,00 m).
2. A parede ganha o vão do tamanho da esquadria, e a janela fica centrada na espessura. A partir daí ela se comporta
   como as janelas do ambiente:
   - anda só no plano da parede, sem sair do segmento;
   - acompanha a espessura no editor de paredes;
   - é apagada junto com a parede.
3. **Desinstalar** deixa a janela solta no mesmo lugar e fecha o vão.

Só paredes do editor de paredes podem receber a janela. Uma parede antiga mostra **Converta a parede pelo editor de
paredes antes de instalar**.

Janelas e portas importadas são acessórios: não entram no plano de corte, a não ser que você marque **Peça de
produção**.
