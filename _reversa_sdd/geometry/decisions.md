# Módulo Geometry, Decisões de Projeto

Este documento cataloga as decisões de projeto e trade-offs técnicos tomados no módulo **geometry** do add-on **BlenderToMob**, documentado no nível **Detalhado**.

---

## 1. Decisão de Usar Graham Scan no Piso Conformal

* **Status**: Aprovado
* **Data da Decisão**: 2026-07-15
* **Contexto**: O piso do ambiente deve preencher dinamicamente a área entre as paredes construídas. Como as paredes são polilinhas soltas e não há estrutura de topologia conectada nativa do Blender que forme automaticamente o loop de contorno fechado para o piso, é necessário derivar o polígono delimitador a partir das coordenadas espaciais das bases das paredes.
* **Decisão**: Utilizou-se o algoritmo Graham Scan (`_convex_hull_2d`) para gerar um fecho convexo contendo todos os vértices de base no plano XY.
* **Alternativas consideradas**:
  - **Construção Manual do Piso pelo Usuário**: Descartado por violar os requisitos do Promob de ajuste conformal automatizado.
  - **Algoritmo Alpha-Shape (Côncavo)**: Permitiria mapear pisos côncavos complexos de salas não-convexas. Descartado devido à alta complexidade de parametrização do raio $\alpha$ sem dependência de pacotes matemáticos robustos como SciPy/NumPy (que não vêm pré-instalados no Python nativo do Blender).
* **Consequências**:
  - *Prós*: Algoritmo leve e robusto que funciona de forma determinística para qualquer cômodo convexo.
  - *Contras*: Incapacidade de mapear layouts em formato côncavo, exigindo criação ou ajuste de pisos côncavos de forma manual. 🟢
