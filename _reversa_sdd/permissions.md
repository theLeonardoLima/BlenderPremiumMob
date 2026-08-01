# Matriz de Acesso e Permissões do Sistema — BlenderToMob

Este documento mapeia o controle de acesso de execução e permissões do add-on **BlenderToMob**, conduzido pelo agente **Detective** no nível de documentação **Detalhado**.

---

## 1. Contexto de Segurança e Execução

O **BlenderToMob** opera como uma extensão embutida dentro do processo principal do Blender 3D. Portanto, ele herda as permissões do usuário que executa o processo do Blender no sistema operacional. No entanto, do ponto de vista da arquitetura de add-ons do Blender, existem restrições de escopo e limites de acesso à API que governam o comportamento dos componentes.

---

## 2. Matriz de Acesso a API e Recursos

| Componente | Acesso à API (`bpy.data`) | Manipulação do Grid / GPU | Escrita no File System | Alteração de Malhas (`bmesh`) | Descrição do Escopo |
|------------|:-------------------------:|:-------------------------:|:----------------------:|:-----------------------------:|---------------------|
| **data** | Leitura/Escrita | - | - | - | Registra e remove tipos de dados e custom properties globais. |
| **geometry** | Leitura/Escrita | - | - | Leitura/Escrita | Gera malhas poligonais de forma imperativa limpando e adicionando vértices/faces. |
| **operators** | Leitura/Escrita | Leitura | - | Leitura/Escrita | Modais interceptam mouse/teclado do sistema e alteram transformações espaciais. |
| **overlays** | Leitura | Leitura/Escrita | - | - | Registra handlers na viewport para desenho gráfico imediato via OpenGL/Vulkan. |
| **ui** | Leitura | - | - | - | Apresenta propriedades na interface gráfica e executa polling ativo de contexto. |
| **cutting** | - | - | Leitura/Escrita | - | Lógica pura Python sem dependência de APIs Blender. Otimiza planos de corte de chapas. |

---

## 3. Classificação de Confiança de Modificações de Malha (Mesh Mutability)

Para evitar vazamentos de memória e corrupção de malhas no Blender (uma vez que operações em background na API `bmesh` sem liberação de dados podem travar a aplicação):

* **Mutação de Geometria de Parede (R-11)**: Apenas permitida via chamadas síncronas em update callbacks ou durante a finalização do operador modal.
* **Mutação de Aberturas (R-12)**: Feita de forma não-destrutiva via modificadores `Boolean` vinculados. O add-on não remove vértices da parede manualmente durante a inserção da porta, garantindo que o histórico da malha e integridade de renderização sejam mantidos.
* **Cálculo de Nesting (R-13)**: Lógica isolada em puro Python que não modifica objetos na cena 3D. Garante estabilidade operacional mesmo sob grandes volumes de peças.
