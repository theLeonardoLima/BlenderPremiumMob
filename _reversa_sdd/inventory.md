# Inventário do Projeto — BlenderToMob

Este documento apresenta o inventário completo do projeto **BlenderToMob**, mapeado pelo agente **Scout** na fase de Reconhecimento.

## 1. Estrutura de Diretórios e Arquivos

Abaixo está a árvore completa de diretórios e arquivos relevantes do add-on (excluindo caches, artefatos temporários e diretórios do Git):

* `build.py` — Script utilitário em Python para empacotar o add-on em um arquivo ZIP
* `blendertomob/` — Diretório raiz do pacote do add-on Blender
  * `blender_manifest.toml` — Manifesto de extensão para Blender 4.2+ (metadados e requisitos)
  * `__init__.py` — Ponto de entrada (register/unregister) que orquestra a inicialização de todos os submódulos
  * `data/` — Camada de dados do add-on
    * `__init__.py` — Registrador local
    * `properties.py` — Definições de PropertyGroups e Custom Properties para paredes, aberturas, módulos e configurações de cena
  * `geometry/` — Camada geométrica e de materiais
    * `__init__.py` — Registrador local
    * `mesh_gen.py` — Funções de modelagem paramétrica via `bmesh` para paredes (retas e polilinhas), piso (convex hull) e módulos
    * `materials.py` — Configuração dinâmica de materiais com Principled BSDF e HSV
  * `operators/` — Camada de comportamentos e interações (Operators)
    * `__init__.py` — Registrador de operadores
    * `wall_builder.py` — Modal Operator interativo de construção de paredes com cota e preview
    * `floor_builder.py` — Operador de ajuste automático de piso e criação manual
    * `opening_builder.py` — Modal Operator interativo de posicionamento, snapping e deslizamento de portas/janelas
    * `cabinet_builder.py` — Inserção de módulos de armário paramétricos
  * `overlays/` — Camada de renderização em viewport via GPU
    * `__init__.py` — Registrador de draw handlers
    * `draw_handlers.py` — Gerenciador de overlays (grade de piso, cota de paredes, destaque de plano de inserção)
  * `ui/` — Camada de apresentação (Interface do Usuário)
    * `__init__.py` — Registrador local
    * `panels.py` — Painéis da Sidebar (Criador de Ambientes, Propriedades, Módulos, Nesting, Configurações)
  * `cutting/` — Lógica algorítmica independente do Blender
    * `__init__.py` — Registrador local
    * `nesting.py` — Otimizador 2D de chapas (guilhotinado / shelf-packing)

## 2. Inventário de Arquivos por Extensão

* **Python (.py):** 18 arquivos (código principal de lógica, operadores, geometria e UI)
* **TOML (.toml):** 1 arquivo (manifesto do add-on do Blender)
* **Markdown (.md):** 1 arquivo (README principal do projeto na raiz)
* **PDF (.pdf):** 1 arquivo (manual de treinamento do Promob de referência de 4.8MB)

## 3. Principais Pontos de Entrada e Configuração

* **`blendertomob/__init__.py`**: Contém o bloco `bl_info` de compatibilidade legada e gerencia o registro global (`register`/`unregister`) chamando as funções dos submódulos em cascata: `data` → `operators` → `ui` → `overlays`.
* **`blendertomob/blender_manifest.toml`**: Define o ID, versão, categoria, tags, requisitos mínimos e localização na interface do View3D do add-on para a nova API de extensões do Blender 4.2+.
