# Algoritmo de Posicionamento e Snapping de Aberturas

Este documento apresenta a análise de fluxo detalhada da lógica matemática e de interações utilizada no posicionamento, deslizamento e transição de portas/janelas nas paredes:

```mermaid
flowchart TD
    A[Gatilho MOUSEMOVE no Modal] --> B[Raycast a partir das coordenadas do cursor]
    B --> C[Calcula intersecção Z=0: mouse_pos_3d]
    
    C --> D[Loop por todas as paredes da cena]
    D --> E[Extrai segmentos da parede e projeta ponto em cada um]
    E --> F[Calcula a menor distância 2D e o fator t de projeção da linha]
    
    F --> G[Identifica o segmento mais próximo de todos os avaliados]
    G --> H[Atualiza target_wall e target_seg_idx]
    
    H --> I[Calcula vetor direção e vetor normal do segmento vencedor]
    I --> J[Projeta raycast no plano vertical da parede para calcular altura Z]
    
    J --> K{Tipo de abertura?}
    K -- DOOR --> L[Trava peitoril sill_height = 0.0]
    K -- WINDOW --> M[Aplica peitoril baseado em P_hit.z: sill = max/min de segurança]
    
    L --> N[Obtém posição final: P_base + Vector Z de peitoril]
    M --> N
    
    N --> O[Cria matriz de rotação 3x3 alinhada aos vetores direção/normal]
    O --> P[Atualiza preview_obj: local, euler, e profundidade baseada na espessura]
    P --> Q[Agenda cota GPU de distância e peitoril]
    Q --> R[Fim do frame modal]
```
```
Fator de Projeção Linear (t):
P = A + t * (B - A)
t = (AP . AB) / |AB|^2  (clamped entre 0.0 e 1.0)
```
```
Cota GPU Visual:
Offset = normal_vector * offset_distance
A_off = A + Offset
B_off = B + Offset
P_off = P_door + Offset
```
