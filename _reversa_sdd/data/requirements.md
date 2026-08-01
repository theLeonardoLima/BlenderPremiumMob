# Módulo Data

## Visão Geral
O módulo **data** define a persistência de estado do add-on, registrando classes `PropertyGroup` e propriedades customizadas nos dados nativos do Blender (`bpy.types.Object`, `bpy.types.Scene`), além de gerenciar os gatilhos de update para reatividade.

## Responsabilidades
- Registrar tipos e schemas paramétricos para paredes, aberturas, armários e configurações de cena.
- Vincular gatilhos de atualização (`update`) para regeneração instantânea de geometria de objetos modificados.
- Preservar o histórico de segmentos polilinhas de paredes usando serialização JSON.

## Regras de Negócio
- **R-01 (Mapeamento de Tipos)**: Objetos com propriedades paramétricas de design CAD devem ser explicitamente categorizados no plano de inserção (`btm_plane.object_kind`). 🟢
- **R-02 (Reatividade de Malha)**: Modificações em dimensões ou espessuras devem forçar a reconstrução da malha geométrica de forma imediata e transparente. 🟢

## Requisitos Funcionais

| ID | Requisito | Prioridade | Critério de Aceite |
|----|-----------|-----------|-------------------|
| RF-01 | Registro de PropertyGroups paramétricos na API `bpy` | Must | Propriedades visíveis no Python Console e acessíveis. |
| RF-02 | Callbacks de atualização de malhas associados a propriedades | Must | Mudar valor na Sidebar atualiza vértices no 3D Viewport. |
| RF-03 | Persistência de segmentos polilinhas no objeto de parede | Must | Custom property `"btm_wall_segments"` salva string JSON válida. |

## Requisitos Não Funcionais

| Tipo | Requisito inferido | Evidência no código | Confiança |
|------|--------------------|---------------------|-----------|
| Portabilidade | Persistência compatível com arquivos padrão `.blend` | `properties.py:353` | 🟢 |

## Critérios de Aceitação

```gherkin
Dado que o usuário tem um armário paramétrico selecionado
Quando ele altera o campo "Largura (mm)" no painel lateral
Então a malha do armário reconstrói-se automaticamente via callback update_cabinet_geom
```

## Prioridade (MoSCoW)

| Requisito | MoSCoW | Justificativa |
|-----------|--------|---------------|
| `BTM_PG_WallSegment` | Must | Estrutura de dados básica das paredes. |
| `BTM_PG_OpeningProperties` | Must | Estrutura de dados básica das portas/janelas. |
| `update_wall_geom` | Must | Reatividade de malhas de paredes. |

## Rastreabilidade de Código

| Arquivo | Função / Classe | Cobertura |
|---------|-----------------|-----------|
| `blendertomob/data/properties.py` | `BTM_PG_WallSegment` | 🟢 |
| `blendertomob/data/properties.py` | `update_wall_geom` | 🟢 |
