# Módulo Cutting, Decisões de Projeto

Este documento cataloga as decisões de projeto e trade-offs técnicos tomados no módulo **cutting** do add-on **BlenderToMob**, documentado no nível **Detalhado**.

---

## 1. Decisão de Usar Algoritmo de Prateleiras (Shelf Packing)

* **Status**: Aprovado
* **Data da Decisão**: 2026-07-15
* **Contexto**: A otimização de planos de corte bidimensionais (2D Bin Packing) é um problema NP-Difícil. A execução no Blender precisa ocorrer de forma instantânea para não travar a interface do usuário. Além disso, marceneiros exigem cortes retilíneos contínuos (corte guilhotinado).
* **Decisão**: Optou-se por utilizar o algoritmo Next-Fit Decreasing adaptado para faixas (prateleiras) de guilhotina:
  - As peças são organizadas em linhas horizontais.
  - A altura de cada linha é determinada pela peça mais alta nela inserida.
  - Isso garante que cortes transversais possam dividir as prateleiras em peças menores sem necessidade de recortes internos ("ninhos").
* **Alternativas consideradas**: Algoritmos baseados em árvores binárias livres (MaxRects). Descartados por gerarem padrões de corte não-guilhotinados inviáveis para serras circulares comuns.
* **Consequências**:
  - *Prós*: Garante cortes executáveis e processamento instantâneo.
  - *Contras*: Pequena redução na eficiência total de aproveitamento da chapa se comparado a layouts livres complexos. 🟢
