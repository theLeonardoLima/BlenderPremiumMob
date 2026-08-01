# Fluxograma do Módulo: Data

Este documento apresenta os diagramas de fluxo do ciclo de dados e reatividade de propriedades do módulo **data**, no nível de documentação **Detalhado**.

---

## 1. Fluxo de Reatividade e Atualização de Geometria

O diagrama abaixo ilustra o ciclo reativo que ocorre quando o usuário modifica uma propriedade paramétrica (como espessura ou pé-direito) no painel de propriedades:

```mermaid
flowchart TD
    A[Modificação de Propriedade na UI] --> B{Propriedade Possui Update Callback?}
    B -- Sim --> C[Executa Callback correspondente]
    B -- Não --> Z[Armazena valor de forma passiva no Blender]
    
    C --> D{Tipo de Objeto?}
    D -- Parede --> E[update_wall_geom]
    D -- Armário --> F[update_cabinet_geom]
    
    E --> G{Possui btm_wall_segments?}
    G -- Sim (Polilinha) --> H[Carrega JSON btm_wall_segments]
    H --> I[Atualiza espessura/altura em todos os segmentos]
    I --> J[Re-salva JSON btm_wall_segments]
    I --> K[Reconstrói polilinha via generate_wall_from_segments]
    G -- Não (Simples) --> L[Reconstrói segmento reto via generate_wall_mesh]
    
    F --> M[Reconstrói caixa via generate_cabinet_mesh]
    
    K --> N[Limpa malha anterior]
    L --> N
    M --> N
    N --> O[Grava novos vértices/faces no bmesh]
    O --> P[Escreve bmesh na malha de destino]
    P --> Q[Força redesenho do viewport 3D]
```
