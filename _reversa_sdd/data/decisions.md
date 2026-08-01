# Módulo Data, Decisões de Projeto

Este documento cataloga as decisões de projeto e trade-offs técnicos tomados no módulo **data** do add-on **BlenderToMob**, documentado no nível **Detalhado**.

---

## 1. Decisão de Persistir Polilinhas em Propriedade String JSON

* **Status**: Aprovado
* **Data da Decisão**: 2026-07-15
* **Contexto**: A modelagem de paredes exige suporte a polilinhas (múltiplos segmentos conectados). O Blender oferece `CollectionProperty` para armazenar listas de PropertyGroups customizadas nos objetos. Contudo, registrar e gerenciar adições, remoções e ordenação em `CollectionProperty` via Python no Blender envolve alta complexidade na API e verbosidade extrema na UI.
* **Decisão**: Optou-se por armazenar a lista estruturada de segmentos como uma string JSON serializada dentro de uma propriedade dinâmica padrão do objeto (`obj["btm_wall_segments"]`).
* **Alternativas consideradas**:
  - **Uso de CollectionProperty nativa**: Exigiria lógica complexa de manipulação de itens e causaria poluição visual nas propriedades dos blocos de dados.
  - **Criar Objetos Blender Diferentes para Cada Segmento**: Aumentaria a contagem de objetos na cena, poluindo a Outliner e complicando a aplicação de modificadores booleanos únicos.
* **Consequências**:
  - *Prós*: Lógica de leitura/escrita extremamente simples e robusta baseada em JSON standard.
  - *Contras*: O arquivo JSON armazenado em string customizada não é validado automaticamente pelo Blender, facilitando corrupção em caso de edições manuais na aba de propriedades customizadas do objeto. 🟢
