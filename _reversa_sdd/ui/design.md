# Módulo UI, Design Técnico

## Interface

As classes herdam de `bpy.types.Panel` e definem o método `draw`:

| Símbolo | Categoria Sidebar | Condição de Visibilidade | Observação |
|---------|------------------|--------------------------|------------|
| `BTM_PT_Environment` | `BlenderToMob` | Sempre visível | Agrupa construtores de paredes. |
| `BTM_PT_FloorSection` | `BlenderToMob` | `len(walls) > 0` | Contém botão para fecho convexo do piso. |
| `BTM_PT_OpeningsSection` | `BlenderToMob` | `len(walls) > 0` | Contém botões de inserção de porta/janela. |
| `BTM_PT_ContextProperties` | `BlenderToMob` | Objeto ativo válido | Exibe propriedades do objeto selecionado. |

## Fluxo Principal — Renderização da UI
1. O Blender redesenha a Sidebar da Viewport 3D.
2. Cada painel registrado executa seu método `draw(self, context)`:
   - Recupera referências globais de cena e objeto ativo via `context.scene` e `context.active_object`.
   - Organiza layouts em colunas (`layout.column()`) e linhas (`layout.row()`).
   - Apresenta campos de propriedades editáveis usando `layout.prop(data, "prop_name")`.
   - Apresenta botões disparadores usando `layout.operator("operator.bl_idname")`.

## Dependências
- `bpy.types.Panel` para definição estrutural de telas no Blender.
- `blendertomob/data/properties.py` para leitura de dados de PropertyGroups.

## Decisões de Design Identificadas

| Decisão | Evidência no código | Confiança |
|---------|---------------------|-----------|
| Polling dinâmico baseado em classificação do objeto | `panels.py:92` | 🟢 |
| Condicionalidade baseada em contagem de paredes da cena | `panels.py:65` | 🟢 |

## Estado Interno
O módulo não mantém estado próprio, agindo apenas como uma camada de exibição (View) direta e reativa dos PropertyGroups da cena e objetos.

## Riscos e Lacunas
- 🟡 Polling muito frequente com loops complexos dentro do método `draw` (ex: varrer todos os objetos da cena buscando paredes a cada frame) pode causar lentidão na interface do Blender. A contagem de paredes deve ser indexada ou cacheada.
