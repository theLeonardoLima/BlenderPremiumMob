# Tasks do Módulo Wall Editor (Editor de Parede 🧱)

## Plano de Implementação

- [x] **WE-T001**: Criar PropertyGroup `HB_Wall_Editor_Props` em `hb_props.py` com todas as propriedades da parede (unidade `mm/cm/m/in/ft`, comprimento, altura, espessura, afastamento, ângulos absoluto/relativo, orientação, incrementos linear/angular, tipo da parede normal/drywall, utilizar valores como padrão). 🟢
- [x] **WE-T002**: Implementar operador modal de desenho interativo `home_builder_walls_OT_interactive_wall_editor` em `operators/walls.py` com snap magnético automático, travamento de vetor angular (45° step), digitação direta numéica e navegação por tecla `TAB`. 🟢
- [x] **WE-T003**: Implementar suporte a unidades de medida dinâmicas (`mm`, `cm`, `m`, `in`, `ft`) e conversão em tempo real nas cotas e painéis de propriedades em `units.py` e `operators/walls.py`. 🟢
- [x] **WE-T004**: Desenvolver o overlay GPU `draw_wall_editor_overlay` em `hb_gpu_draw.py` / `operators/walls.py` com renderização de cotas numéricas na unidade ativa, arco angular vetorizado (0°-360°) e indicador visual de snap. 🟢
- [x] **WE-T005**: Criar o Painel Gráfico de Propriedades e o Menu Suspenso `Editor de Parede 🧱` em `ui/view3d_sidebar.py` e `operators/viewport_hud.py`. 🟢
- [x] **WE-T006**: Conectar a persistência global de padrões (`scene.hb_wall_defaults`) acionada pelo checkbox `Utilizar valores como padrão`. 🟢

