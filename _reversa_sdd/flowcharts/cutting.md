# Fluxograma do Módulo: Cutting

Este documento apresenta o fluxo algorítmico da otimização bidimensional de planos de corte do módulo **cutting**, no nível de documentação **Detalhado**.

---

## 1. Algoritmo de Nesting Bidimensional (`optimize_nesting`)

```mermaid
flowchart TD
    A[Início: optimize_nesting] --> B[Subtrai margem de refilo de todas as chapas]
    B --> C[Filtra e descarta peças que excedem tamanho máximo útil]
    C --> D[Multiplica peças pelo campo quantity: flat_parts]
    D --> E[Ordena flat_parts por área decrescente]
    
    E --> F[Pega próxima peça da lista flat_parts]
    F --> G{Mais peças na lista?}
    
    G -- Sim --> H[Loop pelas chapas de MDF ativas]
    H --> I{Mais chapas?}
    
    I -- Sim --> J[Loop pelas prateleiras/shelves da chapa]
    J --> K{Mais prateleiras?}
    
    K -- Sim --> L{Peça cabe nesta prateleira?}
    L -- Sim --> M[Insere peça no final da prateleira]
    M --> N[Incrementa largura atual, ajusta altura da prateleira e chapa]
    N --> F
    L -- Não --> J
    
    K -- Não --> O{Consegue criar nova prateleira nesta chapa?}
    O -- Sim --> P[Cria prateleira com altura da peça]
    P --> M
    O -- Não --> H
    
    I -- Não --> Q{Inicializa nova chapa de MDF}
    Q --> R[Cria primeira prateleira da chapa com a peça]
    R --> M
    
    G -- Não --> S[Calcula estatísticas de aproveitamento total m²]
    S --> T[Retorna coordenadas X,Y e chapas utilizadas]
    T --> U[Fim]
```
