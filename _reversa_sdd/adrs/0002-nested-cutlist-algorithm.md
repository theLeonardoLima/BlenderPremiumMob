# ADR 0002: Algoritmo de Guilhotina Híbrido com Otimização de Fibra para Nesting

Este registro documenta a decisão arquitetural sobre a lógica de otimização de plano de corte das chapas de mobiliário no módulo **cutting**.

## Status
🟢 **APROVADO**

---

## Contexto
O processo de fabricação de armários de marcenaria exige a fragmentação de chapas inteiras de MDF ($2750 \times 1830$ mm) nas peças de montagem (laterais, fundos, portas). A otimização de plano de corte visa reduzir o desperdício de material. No entanto, duas restrições cruciais governam o problema na marcenaria de pequeno porte:
1. **Corte Guilhotinado**: A maioria das seccionadoras manuais só realiza cortes transversais completos retilíneos de ponta a ponta na chapa. O algoritmo de encaixe de peças deve respeitar essa restrição física de maquinário.
2. **Sentido do Veio (Fibras da Madeira)**: Peças amadeiradas têm texturas com direção visual fixa. Rotacionar certas peças em 90° pode arruinar o acabamento visual do mobiliário.

---

## Decisão
Implementou-se um otimizador bidimensional em puro Python utilizando a heurística **Next-Fit Decreasing com Divisão em Prateleiras (Shelf Packing)** simulando cortes de guilhotina:
1. Ordenação prévia de todas as peças por área de corte decrescente.
2. Divisão da chapa de MDF em faixas horizontais (prateleiras), onde a altura de cada faixa é travada pela primeira e maior peça colocada nela.
3. Desconto sistemático de margens de refilo (10mm nas bordas da chapa) e kerf (4mm de consumo da lâmina de corte).
4. Restrição de rotação de 90° vinculada à propriedade `grain_direction` da peça (`NONE` permite rotação, `VERTICAL` e `HORIZONTAL` travam a orientação).

---

## Alternativas Consideradas
* **Algoritmos Genéticos ou Programação Linear Inteira (MILP)**: Encontrariam o arranjo matematicamente perfeito. Contudo, apresentam tempo de processamento exponencial, o que bloquearia a UI do Blender por vários segundos, e possuem alta complexidade de codificação sem bibliotecas externas C++ pesadas.
* **Guillotine-Cut 2D de Nível Livre (Bin-Packing Livre)**: Ignorar as faixas horizontais de prateleiras. Aumentaria ligeiramente o aproveitamento de material, mas geraria planos com layouts de cortes complexos ("ninhos") impossíveis de serem executados em seccionadoras verticais simples.

---

## Consequências
* **Prós**:
  * Execução instantânea (sub-segundo) diretamente em Python puro dentro do Blender.
  * Planos de corte 100% executáveis em serras circulares manuais ou seccionadoras de guilhotina.
  * Preservação correta da estética do veio da madeira.
* **Contras**:
  * Aproveitamento ligeiramente menor (eficiência cerca de 5-10% menor) em relação a algoritmos matemáticos exatos de bin-packing livre.
