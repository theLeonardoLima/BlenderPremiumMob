# Onboarding: janela OBJ com folhas de correr (007)

Pré-requisito: `python3 build.py`, instalar `caffmob_draw.zip` no Blender 5.2 e abrir um projeto com uma parede
(Construir › Desenhar Paredes).

## 1. Importar

1. Use Inserir › **Importar modelo 3D** e escolha `_reversa_forward/007-janela-obj-folhas-colisao/inputs/janela_preta_1400mm.obj`.
2. Deixe **Unidade: Automática** e **Eixo vertical: Z**.
3. Confira: a janela aparece em pé, com 1400 × 850 × 80 mm (N › Item › Dimensões), e o relatório diz "unidade: mm".

## 2. Montar a esquadria

1. Com as peças importadas selecionadas, use **Montar esquadria**.
2. O diálogo mostra três grupos: Folha_Esquerda (15), Folha_Direita (15) e Esquadria (16). Confirme.
3. Selecione a folha esquerda. O painel mostra Correr, Sentido "Para a esquerda" e o aviso "Pouco curso para este
   lado: inverta o sentido".
4. Troque o sentido para "Para a direita". O curso passa a ser a distância livre até o marco direito.

## 3. Abrir e fechar

1. Leve a barra **Abertura** a 100%. A folha corre e para encostada no marco direito; o painel diz "Folha bateu em
   Marco_Externo_Direita" e a peça aparece destacada.
2. Volte a 0%. A folha para exatamente na posição do arquivo.
3. Inverta também a folha direita e abra a 40%. Abra a esquerda a 80% e leve a esquerda a 0%: ela para encostada no
   montante da direita, e o painel diz "Folha encostou em Folha_Direita".

## 4. Parede

1. Selecione a esquadria e a parede e use **Instalar na parede**. O vão aparece na parede e a janela fica nele.
2. Arraste a janela: ela anda só no plano da parede e não sai do segmento.
3. Use **Desinstalar**. A janela fica solta e o vão fecha.
4. Ctrl+Z desfaz cada operação num passo.

## 5. Testes automáticos

```bash
cd tests && python3 -m unittest test_import_units test_grouping test_slide_limits test_i18n_coverage && cd ..
ruff check caffmob_draw/ && python3 docs/rag/tools/check_api.py
blender --background --factory-startup --python-exit-code 1 --python tests/blender_007_window_smoke.py
```
