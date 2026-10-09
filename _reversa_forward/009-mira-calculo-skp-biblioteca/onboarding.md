# Onboarding: testar a 009 pela primeira vez

> Para quem vai validar a feature no Blender 5.2, com o pacote gerado por `python3 build.py` e instalado em
> Edit › Preferences › Get Extensions › Install from Disk.

## 1. Mira e alinhamento (editor de paredes)

1. Desenhe um cômodo retangular de 3000 × 2500 mm e abra o **Editor de Paredes**.
2. Escolha o lápis. Uma cruz fina acompanha o cursor pela vista inteira.
3. Comece uma parede fora do cômodo, mais ou menos na altura do canto de cima. Ao chegar a uns 8 px na tela da altura
   do canto:
   - a linha horizontal fica destacada;
   - aparece uma guia tracejada até o canto, com um anel nele.
4. Clique. Selecione o ponto criado: a coordenada Y é igual à do canto.
5. Segure Shift: as travas de alinhamento somem enquanto ele estiver apertado.

## 2. Medidas com conta e direção travada

1. No lápis, clique o ponto inicial e mova o mouse para a direita: a seta mostra "→ 0°".
2. Digite `100` e Enter, depois `285` e Enter. Mova o mouse para qualquer lado, sem clicar, e siga com `2*8`, `200/2`
   e `2000`, cada um com Enter.
   - Ao digitar `2*8`, aparece "= 16 mm" ao lado.
   - Saem cinco trechos seguidos para a direita, que somam 2501 mm.
3. Aperte ↑ e digite `1200` e Enter: o trecho sobe 1200 mm.
4. Clique à esquerda do último ponto (com a trava ortogonal): o clique cria o trecho até lá, e o próximo `500` Enter
   vai para a esquerda.
5. Digite `10/0` e Enter: aparece "Valor Inválido", e nada é criado. O Esc limpa o texto.

## 3. Biblioteca de objetos

1. Abra **Inserir › Objetos**. Há 7 categorias, e os itens embutidos ficam em Portas, Janelas, Cooktops, Mesas e
   Decoração.
2. Insira a **Porta lisa 80**: ela aparece no cursor 3D e acompanha o mouse; um clique solta. Na seção Selecionado, a
   barra de abertura gira a folha até 90°.
3. Insira a **Mesa 120 × 80** e calcule o plano de corte: o tampo aparece na lista de peças.
4. Selecione o tampo e use **Retexturizar › Acabamento** para trocá-lo para um material do plugin. Depois use
   **Imagem própria** com um JPG de madeira, tamanho 600 mm: o veio aparece em escala real, sem esticar.
5. Importe um OBJ ou glTF qualquer por **Importar modelo**. Converta uma parte em folha e use **Acrescentar à
   biblioteca** em "Decoração", com o nome "Meu teste". Reinicie o Blender: o item continua lá e volta com a folha.
6. Tente acrescentar de novo com o mesmo nome: o diálogo oferece Substituir ou Renomear.

## 4. SketchUp

1. Em **Importar modelo**, escolha um `.skp` (o teste usa `tests/fixtures/porta_teste.skp`, gerado pelo OpenSKP).
2. A porta entra com os grupos "Batente 1" e "Folha 1", na escala certa (confira com a régua).
3. Os materiais vêm com os nomes do SketchUp ("Branco", "Madeira"), e a folha mostra a textura.
4. Converta a folha em folha de giro e acrescente o item à sua biblioteca, com a origem "3D Warehouse: <autor>" se
   veio de lá.
5. Tente um arquivo corrompido (por exemplo, um `.txt` renomeado para `.skp`): aparece o motivo e a alternativa, e
   nada é criado.

## 5. Verificações automáticas

```bash
cd tests && python3 -m unittest discover -p "test_*.py"
ruff check caffmob_draw/
python3 docs/rag/tools/check_api.py
xvfb-run -a blender --factory-startup --enable-event-simulate --python tests/blender_009_walls_smoke.py
blender --background --factory-startup --python-exit-code 1 --python tests/blender_009_library_smoke.py
blender --background --factory-startup --python-exit-code 1 --python tests/blender_009_skp_smoke.py
```
