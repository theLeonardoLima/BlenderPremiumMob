# Módulo Overlays, Decisões de Projeto

Este documento cataloga as decisões de projeto e trade-offs técnicos tomados no módulo **overlays** do add-on **BlenderToMob**, documentado no nível **Detalhado**.

---

## 1. Decisão de Usar API gpu e shader 2D/3D Built-in do Blender

* **Status**: Aprovado
* **Data da Decisão**: 2026-07-15
* **Contexto**: A viewport 3D precisa renderizar guias CAD (linhas de cota, caixas transparentes, texto bitmap). Antigamente, isso era feito com o módulo legado `bgl` (OpenGL bruto). A partir do Blender 4.0, o módulo `bgl` foi depreciado em prol da abstração multiplataforma `gpu` para dar suporte a pipelines gráficos modernos como Vulkan e Metal.
* **Decisão**: Optou-se por utilizar o módulo `gpu` com shaders built-in (`from_builtin('UNIFORM_COLOR')` e `from_builtin('POLYLINE_UNIFORM_COLOR')`) organizando geometrias em lotes de lotes (`gpu.types.GPUBatch`).
* **Alternativas consideradas**:
  - **Uso de Objetos Temporários da Cena**: Instanciar malhas de seta e texto reais na cena. Descartado porque sobrecarregaria a árvore de objetos e degradaria performance geral da viewport.
  - **Manter Módulo bgl Legado**: Descartado por causar quebras de compatibilidade imediatas no Blender 4.0+ e inviabilizar o add-on no macOS (Vulkan/Metal).
* **Consequências**:
  - *Prós*: Renderização extremamente leve com aceleração por hardware direta na GPU.
  - *Contras*: Sintaxe verbosa para compilar lotes geométricos em Python e dependência direta de alterações futuras nas definições de shaders internos do Blender. 🟢
