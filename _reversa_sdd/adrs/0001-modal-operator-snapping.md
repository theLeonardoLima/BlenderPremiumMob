# ADR 0001: Modal Operators com Snapping Dinâmico para Construtores

Este registro documenta a decisão arquitetural sobre a implementação das ferramentas interativas de desenho CAD (construção de paredes e inserção de vãos) no add-on **BlenderToMob**.

## Status
🟢 **APROVADO**

---

## Contexto
A modelagem paramétrica tradicional no Blender se apoia em operadores estáticos (o usuário altera valores numéricos em caixas de diálogo pós-criação). Contudo, a experiência do sistema Promob exige uma interação fluida direta na viewport 3D:
1. Ao construir paredes, o usuário clica sequencialmente no piso, visualizando linhas guias dinâmicas e cotas reais antes de confirmar.
2. Ao inserir portas e janelas, as aberturas devem deslizar ao longo das paredes, travando-se no alinhamento espacial e pulando para paredes vizinhas ao contornar quinas.

---

## Decisão
Optou-se por utilizar **Modal Operators** (`bpy.types.Operator` executando lógica em loops contínuos no método `modal()`), acoplados a:
1. **Raycasting de Cursor**: Projeta a coordenada bidimensional da tela na cena 3D usando `bpy_extras.view3d_utils`.
2. **Snapping por Menor Distância 2D**: Computa a projeção do cursor contra os vetores diretores de todas as paredes ativas da cena e escolhe o segmento vencedor.
3. **GPU Immediate Drawing**: Registra handlers na viewport para desenhar cotas dinâmicas, pontos de snap e previews transparentes de cor verde/ciano sem instanciar geometrias reais no Blender antes da confirmação.

---

## Alternativas Consideradas
* **Operadores Estáticos Padrão do Blender**: Exigiriam que o usuário inserisse a parede em coordenadas globais (X, Y, Z) e depois digitasse o comprimento e rotação no painel lateral. Descartado por violar os requisitos de usabilidade do Promob.
* **Gizmos Personalizados**: Usar o sistema de Gizmos do Blender para esticar as paredes. Descartado devido à complexidade de manipulação de polilinhas fechadas e snap dinâmico de quinas em lote.

---

## Consequências
* **Prós**:
  * Usabilidade idêntica ao CAD Promob.
  * Preview leve e instantâneo sem poluir o histórico de desfazer (Undo) com objetos lixo temporários.
  * Snapping dinâmico robusto e intuitivo de quinas e peitoris.
* **Contras**:
  * Aumento da complexidade matemática do código (projeções ponto-segmento, interseções raio-plano, rotações matriciais 3x3).
  * Necessidade de tratamento rigoroso de liberação de memória dos draw handlers da GPU (`POST_VIEW`) para evitar travamentos do Blender.
