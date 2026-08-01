# Fluxograma do Módulo: Operators

Este documento apresenta o fluxo de orquestração de eventos modais do módulo **operators**, no nível de documentação **Detalhado**.

---

## 1. Loop Modal do Construtor de Parede (`BTM_OT_WallBuilder`)

Abaixo está o ciclo de vida do operador modal de paredes que captura interações em tempo real no 3D Viewport:

```mermaid
flowchart TD
    A[Início: invoke] --> B[Adiciona draw_handler de preview]
    B --> C[Adiciona modal_handler do Blender]
    C --> D[Retorna RUNNING_MODAL]
    
    D --> E{Evento detectado no modal?}
    
    E -- MOUSEMOVE (sem clique) --> F[Raycast mouse -> Z=0]
    F --> G[Atualiza comprimento/ângulo sob cursor]
    G --> H[Agenda redesenho de preview]
    H --> D
    
    E -- LEFTMOUSE (Pressionado) --> I{Building ativo?}
    I -- Não --> J[Inicia construção: marca primeiro vértice]
    J --> H
    I -- Sim --> K[Confirma segmento atual: _confirm_segment]
    K --> L{Vértice próximo ao inicial?}
    L -- Sim --> M[Snappa ao ponto inicial: fecha loop]
    M --> N[Executa _finish: gera malha final]
    N --> O[Limpa draw_handler e desvincula modal]
    O --> P[Fim: CANCELLED ou FINISHED]
    L -- Não --> Q[Move origem para ponto final, zera comprimento]
    Q --> H
    
    E -- Teclado (0-9, ., -) --> R[Adiciona tecla ao buffer de digitação]
    R --> S[Ativa modo typing = True]
    S --> H
    
    E -- TAB --> T[Alterna campo ativo: Length / Angle / Thickness / Height]
    T --> H
    
    E -- ENTER --> U{typing ativo?}
    U -- Sim --> V[Aplica buffer numérico ao campo ativo: _commit_typed_value]
    V --> W[typing = False, limpa buffer]
    W --> H
    U -- Não --> K
    
    E -- ESC ou RMB --> X[Executa _cleanup]
    X --> O
```
