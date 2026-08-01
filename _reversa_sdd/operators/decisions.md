# Módulo Operators, Decisões de Projeto

Este documento cataloga as decisões de projeto e trade-offs técnicos tomados no módulo **operators** do add-on **BlenderToMob**, documentado no nível **Detalhado**.

---

## 1. Decisão de Máquina de Estado Baseada em Eventos no Loop Modal

* **Status**: Aprovado
* **Data da Decisão**: 2026-07-15
* **Contexto**: O Blender 3D Viewport possui um loop de eventos baseado em polling de frames. Operadores que interagem com o mouse e teclado em tempo real devem rodar de forma não-bloqueante para permitir que o usuário rotacione a câmera enquanto desenha ou arrasta objetos.
* **Decisão**: Utilizou-se o método `modal()` para gerenciar eventos do Blender (`event.type` e `event.value`), com a seguinte separação de estados:
  - Eventos de mouse (`MOUSEMOVE`) atualizam coordenadas de snap.
  - Eventos de teclado (`ZERO` a `NINE`) são desviados para um acumulador de texto (`typed_value`) apenas se o usuário estiver digitando ativamente, retornando `{'RUNNING_MODAL'}` para bloquear o consumo das teclas pelo Blender.
  - Outros eventos (ex: clique do meio do mouse para rotacionar câmera) retornam `{'PASS_THROUGH'}`, permitindo a navegação 3D nativa do Blender durante o desenho do ambiente.
* **Alternativas consideradas**: Bloquear todos os eventos durante a construção. Descartado porque o usuário não conseguiria girar a câmera em ambientes apertados.
* **Consequências**:
  - *Prós*: Excelente usabilidade e navegação de câmera livre durante a edição paramétrica.
  - *Contras*: Risco de falsos inputs de atalhos do Blender se o consumo de teclas (`PASS_THROUGH` vs `RUNNING_MODAL`) não for gerenciado com precisão cirúrgica. 🟢
