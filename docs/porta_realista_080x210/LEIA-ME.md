# Porta de madeira com portal — 80 × 210 cm

Modelo original criado para visualização arquitetônica, inspirado apenas nas dimensões do nome da referência `PORTA+0_80X2_10.skp`; não é uma conversão desse arquivo.

## Importar no Blender

1. Arquivo → Importar → Wavefront (.obj).
2. Selecione `porta_realista_080x210.obj`.
3. Mantenha escala **1**, frente **-Z** e cima **Y** (padrões do importador).
4. Use Material Preview ou Rendered para visualizar os materiais.

Mantenha o `.mtl` e os dois PNGs junto do OBJ. A folha está fechada no OBJ e as peças estão separadas por nome. O arquivo `.blend` adicional contém uma apresentação entreaberta, iluminação, câmera e texturas incorporadas.

## Dimensões e componentes

- Unidades: metros. Folha: 0,800 × 2,100 × 0,040 m.
- Parte inferior da folha a 8 mm do piso. Espessura do marco: 145 mm.
- Portal completo: aproximadamente 0,958 m de largura e 2,216 m de altura.
- Marco, batentes, guarnições e filetes em ambas as faces.
- Folha com duas almofadas rebaixadas e frisos, veios orientados por peça.
- Três dobradiças com nós e parafusos de cabeça cruzada.
- Maçanetas de alavanca, rosetas, cilindros, lingueta e espelhos metálicos.
- Vedações laterais, superior e inferior; bordas chanfradas.

Texturas de madeira originais de 1024 × 2048 pixels, cor e rugosidade. O MTL utiliza extensões PBR para metais e rugosidade. Microrelevo e acabamento completo estão na cena Blender; leitores OBJ diferentes podem interpretar materiais de modo diferente. OBJ não transporta pivôs, hierarquias, drivers ou animação. Ferragens são representações visuais, sem mecanismo interno de fechadura ou certificação para fabricação.

`gerar_porta.py` permite regenerar o conjunto numa instância dedicada do Blender. Ele limpa a cena dessa instância: execute em background, não sobre um projeto aberto.
