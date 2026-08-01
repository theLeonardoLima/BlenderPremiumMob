# Módulo Overlays, Tarefas de Implementação

## Pré-requisitos
- Módulo `data` registrado e ativo.

## Tarefas

- [ ] T-01, Implementar desenho de grade visual na GPU
  - Origem no legado: `overlays/draw_handlers.py:44`
  - Critério de pronto: Linhas e pontos de grade renderizados na Viewport Z=0.
  - Confiança: 🟢
- [ ] T-02, Implementar destaque do plano sob cursor
  - Origem no legado: `overlays/draw_handlers.py:192`
  - Critério de pronto: Destaque amarelo translúcido sobre planos de inserção ativos.
  - Confiança: 🟢
- [ ] T-03, Implementar desenho de cotas lineares
  - Origem no legado: `overlays/draw_handlers.py:240`
  - Critério de pronto: Cotas e etiquetas com medidas reais são exibidas nas laterais de paredes e aberturas.
  - Confiança: 🟢

## Tarefas de Teste

- [ ] TT-01, Testar vazamento de memória (Memory Leak) registrando e desregistrando handlers da GPU repetidamente no viewport
- [ ] TT-02, Verificar consistência de renderização de cotas sob mudanças de escala ou zoom na viewport 3D do Blender
