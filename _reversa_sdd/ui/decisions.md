# Módulo UI, Decisões de Projeto

Este documento cataloga as decisões de projeto e trade-offs técnicos tomados no módulo **ui** do add-on **BlenderToMob**, documentado no nível **Detalhado**.

---

## 1. Decisão de Usar a Sidebar (View3D) como Principal Ponto de Entrada da Interface

* **Status**: Aprovado
* **Data da Decisão**: 2026-07-15
* **Contexto**: O add-on BlenderToMob precisa expor controles de desenho CAD de fácil acesso ao projetista de marcenaria. O Blender 3D oferece múltiplos locais de inserção de UI:
  - Aba de propriedades do objeto (`Properties Editor`).
  - Menus flutuantes no topo da Viewport (`Header`).
  - Barra de ferramentas lateral da Viewport 3D (`Sidebar` - tecla N).
* **Decisão**: Optou-se por consolidar todas as telas e botões na barra lateral `Sidebar` do View3D sob a aba única `BlenderToMob`.
* **Alternativas consideradas**:
  - **Uso do Properties Editor (Aba de Objetos)**: Descartado por exigir que o usuário mude constantemente de janela ou editor para acionar ferramentas que rodam diretamente na Viewport, quebrando o fluxo de modelagem contínua.
  - **Menu Flutuante no Topo (Header)**: Descartado pela limitação extrema de espaço para campos numéricos de parametrização e tabelas de nesting.
* **Consequências**:
  - *Prós*: Mantém as ferramentas acessíveis diretamente ao lado da área de trabalho 3D, facilitando a alteração de parâmetros em tempo real.
  - *Contras*: Se muitos add-ons do usuário utilizarem a Sidebar, a barra lateral pode ficar poluída com muitas abas verticais, dificultando a localização da aba do add-on. 🟢
