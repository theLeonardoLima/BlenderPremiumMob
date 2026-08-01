# Módulo Geometry, Tarefas de Implementação

## Pré-requisitos
- Módulo `data` registrado e ativo na cena.

## Tarefas

- [ ] T-01, Implementar geração de parede paramétrica polilinha
  - Origem no legado: `geometry/mesh_gen.py:57`
  - Critério de pronto: Extrusão lateral e vertical no bmesh baseada em coordenadas de início e fim.
  - Confiança: 🟢
- [ ] T-02, Implementar Convex Hull 2D para piso automático
  - Origem no legado: `geometry/mesh_gen.py:123`
  - Critério de pronto: Identifica vértices de base em coordenadas de mundo e fecha polígono.
  - Confiança: 🟢
- [ ] T-03, Implementar malha estrutural do armário MDF
  - Origem no legado: `geometry/mesh_gen.py:294`
  - Critério de pronto: Caixa com laterais, tampo, base e fundo modelados de forma isolada respeitando a espessura.
  - Confiança: 🟢

## Tarefas de Teste

- [ ] TT-01, Testar regeneração de malha de armário com larguras e espessuras extremas (ex: 3000mm largura, 50mm chapa)
- [ ] TT-02, Validar se a face gerada para o piso é plana e está localizada na altura Z=0.0
