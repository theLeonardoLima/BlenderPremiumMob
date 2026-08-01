# Fluxograma do Módulo: UI

Este documento apresenta a estrutura de renderização em árvore do painel Sidebar do módulo **ui**, no nível de documentação **Detalhado**.

---

## 1. Hierarquia de Panels na Sidebar (BlenderToMob category)

Abaixo está o mapeamento de agrupamento visual e reatividade condicional do layout Sidebar:

```mermaid
flowchart TD
    A[Sidebar: BlenderToMob Category] --> B[PT_EnvironmentBuilder: Criador de Ambientes]
    
    B --> C[PT_WallConstruction: Construção de Parede]
    
    B --> D{Há paredes na cena?}
    D -- Sim --> E[PT_FloorSection: Piso]
    D -- Sim --> F[PT_OpeningsSection: Aberturas]
    D -- Não --> Z[Oculta Piso e Aberturas panels]
    
    B --> G[PT_InsertionPlane: Plano de Inserção]
    
    A --> H[PT_ContextProperties: Painel de Propriedades Reativo]
    H --> I{Objeto Ativo Selecionado?}
    I -- Parede --> J[Exibe espessura, comprimento, altura da parede]
    I -- Armário --> K[Exibe largura, altura, profundidade, chapa do armário]
    I -- Abertura --> L[Exibe tipo, peitoril, largura, altura do vão]
    I -- Nenhum/Outro --> M[Exibe label: Nenhum objeto de design selecionado]
    
    A --> N[PT_FurniturePanel: Inserção de Módulos]
    A --> O[PT_NestingPanel: Plano de Corte/Otimização]
    A --> P[PT_GlobalSettings: Snaps e Configurações de Overlays]
```
