# Fluxograma do Módulo: Geometry

Este documento apresenta o fluxo de geração e modelagem poligonal paramétrica de baixo nível do módulo **geometry**, no nível de documentação **Detalhado**.

---

## 1. Geração Paramétrica de Parede

Ilustra o fluxo da função `generate_wall_from_segments`:

```mermaid
flowchart TD
    A[Início: generate_wall_from_segments] --> B[Limpar malha antiga: clear_mesh]
    B --> C[Inicializar novo bmesh]
    C --> D[Loop por cada segmento da lista]
    D --> E{Há mais segmentos?}
    
    E -- Sim --> F[Converte coordenadas de mm para metros]
    F --> G[Calcula vetor direção e vetor normal]
    G --> H[Extrui a largura nas duas direções da normal]
    H --> I[Cria os 4 vértices inferiores do plano de base]
    I --> J[Cria a face inferior da base: bm.faces.new]
    J --> K[Extrui a face para cima: extrude_face_region]
    K --> L[Translada os vértices extrudados na altura H]
    L --> D
    
    E -- Não --> M[Recalcula normais das faces para fora]
    M --> N[Grava bmesh na malha do objeto]
    N --> O[Libera memória do bmesh]
    O --> P[Atualiza objeto no Blender: data.update]
    P --> Q[Fim]
```
