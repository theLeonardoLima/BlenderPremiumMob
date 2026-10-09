# Onboarding: testar a 010

> Pacote gerado por `python3 build.py` e instalado no Blender 5.2.

## 1. Porta real

1. Desenhe um cômodo com paredes de 150 mm. Em **Construir › Aberturas**, coloque uma **porta**.
2. A porta sai com 80 × 210 cm:
   - marco e guarnições nos dois lados;
   - folha de nogueira com duas almofadas;
   - maçanetas e 3 dobradiças.

   Não há caixa sólida nem texto "DOOR"; a caixa de referência aparece só em arame.
3. Na seção **Selecionado**, use a barra de abertura: a folha gira até 90°. Coloque um armário perto da dobradiça:
   a folha para nele.
4. Nos prompts da porta, mude a largura para 90: folha e marco se refazem, e a maçaneta não muda de tamanho.
5. No editor de paredes, mude a espessura da parede para 200 mm e dê OK: o marco acompanha.
6. Coloque uma **porta dupla** (160 × 210) e um **vão aberto**: duas folhas no primeiro; só marco e guarnições no
   segundo.
7. Abra um arquivo antigo com portas em caixa: a barra lateral oferece **Atualizar portas e janelas**.

## 2. Janela real

Coloque uma janela de 120 × 100. Ela tem:
- marco de alumínio;
- 2 folhas de correr com vidro;
- trilhos, puxadores e peitoril.

As folhas correm até o batente.

## 3. Modo de vista

Em **Construir**, escolha **Textura** e ligue **Linhas**: madeira com as arestas de todos os objetos. Desligue Linhas
e depois volte a **Sólido**. Salve e reabra: o modo continua.

## 4. SketchUp

Importe `tests/fixtures/porta_aninhada.skp`:
- a folha chega com as 4 ferragens dentro do grupo dela;
- a figura de escala não entra, e o relatório avisa;
- importe de novo: continua um material só, chamado "Layer0".

## 5. Verificações automáticas

```bash
cd tests && python3 -m unittest discover -p "test_*.py"
ruff check caffmob_draw/ && python3 docs/rag/tools/check_api.py
blender --background --factory-startup --python-exit-code 1 --python tests/blender_010_openings_smoke.py
blender --background --factory-startup --python-exit-code 1 --python tests/blender_010_view_mode_smoke.py
blender --background --factory-startup --python-exit-code 1 --python tests/blender_010_skp_tree_smoke.py
```
