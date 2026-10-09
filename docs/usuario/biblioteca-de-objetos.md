# Biblioteca de objetos e SketchUp

Guia para inserir portas, janelas, cooktops, mesas e decoração prontos e para guardar os seus próprios objetos,
inclusive os que vêm do SketchUp, já com a folha da porta, as chapas de produção e as texturas configuradas.

## 1. Inserir um objeto

Abra **Inserir › Objetos**, na barra lateral.

1. Escolha a categoria na fileira de ícones: **Portas**, **Janelas**, **Cooktops e eletros**, **Mesas**, **Cadeiras e
   assentos**, **Decoração** ou **Outros**. O nome da categoria ativa aparece embaixo.
2. Para achar pelo nome, digite parte dele em **Buscar**.
3. Clique no nome do objeto. Ele aparece no cursor 3D e acompanha o mouse pelo chão. Um **clique** solta o objeto no
   lugar; **Esc** ou o botão direito cancelam e o tiram da cena. A roda e o botão do meio continuam mexendo na vista.

Objetos que vêm com o plugin:
- **Porta lisa 80**, com folha de giro até 90°;
- **Janela de correr 120**, com duas folhas de correr;
- **Cooktop 4 bocas**;
- **Mesa 120 x 80**, com o tampo como peça de produção;
- **Vaso com planta**;
- **Quadro 60 x 80**.

A folha da porta e as da janela abrem pela barra de abertura na seção **Selecionado** e param ao esbarrar em
paredes, móveis e no batente, como os agregados. O tampo da mesa entra no plano de corte.

## 2. Guardar os seus objetos

Selecione o objeto (ou as peças dele) e use **Acrescentar à biblioteca**, no fim de **Inserir › Objetos**.

- **Nome** e **Categoria:** onde ele vai aparecer.
- **Origem**, **Autor** e **Licença:** de onde o modelo veio, para não perder a autoria (exemplo de origem:
  "3D Warehouse: <autor>").
- **Arquivo** (opcional): em vez da seleção, um OBJ, FBX, glTF/GLB ou SketchUp, que é importado e guardado direto.
- **Nome repetido**, quando já existe um objeto seu com o mesmo nome na categoria: **Renomear** salva como
  "<nome> 2"; **Substituir** regrava o objeto.

Tudo o que você configurou vai junto:
- grupos de peças;
- esquadria e folhas de porta (giro ou correr), com o curso e os batentes;
- agregados;
- peças de produção;
- materiais e texturas.

Inserido de novo, em outro projeto, o objeto volta pronto. Os seus objetos ficam na sua pasta de usuário do plugin e
continuam lá depois de atualizar o plugin. O **✕** ao lado do nome apaga um objeto seu; os que vêm com o plugin não
podem ser apagados.

## 3. Retexturizar

Com peças selecionadas, a seção **Selecionado** mostra **Retexturizar**:
- **Acabamento:** escolha na lista os materiais das bibliotecas de chapas do plugin (frameless, face frame, closets)
  ou os que já estão no projeto. Nas chapas de produção, o material vai para as duas faces.
- **Imagem:** use uma foto ou textura sua (PNG, JPG, TIFF, WebP) e diga quanto ela mede de verdade, por exemplo
  600 mm. A imagem é aplicada em escala real e em projeção de caixa: não estica, mesmo em modelos importados sem
  mapeamento.

Cada um tem duas opções: **Parte selecionada** (só as peças selecionadas) ou **Item inteiro** (todas as peças do
objeto). A troca vale para aquela cópia na cena; para guardar, acrescente-o de novo à biblioteca, com **Substituir**.

## 4. SketchUp (.skp)

Em **Importar modelo 3D** (ou no campo **Arquivo** de Acrescentar à biblioteca), escolha um arquivo `.skp`. Funciona
em Linux, Windows e macOS, sem o SketchUp instalado.

- Cada componente ou grupo do SketchUp vira um **grupo de peças** com o nome dele, na escala certa e em pé.
- A **hierarquia** é mantida: um componente dentro de outro vira um grupo dentro do grupo do pai. Numa porta, as
  dobradiças e a maçaneta ficam dentro da folha e vão junto quando ela vira folha de porta.
- **Figuras de escala** do SketchUp (as pessoas em 2D, como "2D_Woman_…") não entram. O aviso da importação diz
  quantas foram ignoradas.
- Os materiais mantêm os **nomes do SketchUp**, e as texturas vêm junto, guardadas dentro do projeto. Importar o mesmo
  arquivo de novo reaproveita os materiais, sem criar cópias. Um material de camada (`Layer_Layer0`) fica com o nome
  da camada (`Layer0`).
- Depois, converta o que precisar: a folha em folha de porta (giro ou correr), a esquadria em batente, uma chapa em
  peça de produção. Em seguida, acrescente o objeto à sua biblioteca.

Versões: arquivos do SketchUp 2021 em diante abrem por completo. Dos arquivos de 2013 a 2020, cerca de 1 em cada 4
não abre. Nesse caso aparece o motivo, e nada é criado. Abra o arquivo no SketchUp e salve numa versão recente, ou
exporte em glTF, OBJ ou FBX.

## 5. Modelos do 3D Warehouse e licença

Você pode baixar modelos do [3D Warehouse](https://3dwarehouse.sketchup.com/) com a sua conta Trimble e usá-los nos
seus projetos, inclusive comerciais. A licença deles **não permite** juntar modelos baixados de lá numa biblioteca
para redistribuir. Por isso:
- o plugin não traz modelos do 3D Warehouse;
- os modelos que você baixa ficam só na **sua** biblioteca local;
- ao acrescentar um modelo de lá, preencha a **Origem** com o autor, para manter a autoria.
