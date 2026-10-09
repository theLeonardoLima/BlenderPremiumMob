# Investigation: 008-editor-armario-construtor

> Data: `2026-10-08`. Fontes: `inputs/elicitacao-construtor-de-armarios-v2.md`, as 20 capturas de `inputs/` e o código
> de `caffmob_draw/`.

## 1. O que o Construtor mostra (capturas)

| Captura | Elemento | Usado em |
|---|---|---|
| TELA INICIAL 001 | Tipo; Definições (vãos, largura, altura, profundidade); Posição (Livre + 4 cotas, desabilitadas); árvore de componentes com caixas e valores; Movimentação (Passo inicial 0, Passo 10); OK/Cancelar/Aplicar (Aplicar desabilitado); "Selecionado: (nenhum)"; cotas 800/2250/770 | I2, I6 |
| DIVISOES 001 | Vertical/Horizontal/Inserção múltipla; Móveis/Fixas/Distanciador/Sem Divisória; Com/Sem Recuo Frontal; miniaturas "Interna s/ Recuo Tras 15mm" e "Interna c/ Recuo Tras 15mm"; Inserir desabilitado sem vão | I3 |
| GAVETAS 001 | Vão em vermelho, cotas 340/1880; Gavetas/Gavetões/Internas/Blum; Opções de gavetas, de frentes e de inserção (4); "Não há propriedades disponíveis!"; "Selecionado: Vão" | I2, I3 |
| PORTAS 001 | Inferior/Superior/Alta/Basculante; Ambas/Inteira/Esquerda/Direita; grade de 12+ estilos; Inserir invertido; linhas de abertura tracejadas | I3 |
| FUNDO 001 | Inteiro / Inteiro Recuado; "Inserir automaticamente" marcado; Fundo Inteiro 15mm; fundo pintado na vista | I3 |
| INTERNOS 001 | Painel p/ Eletros / Biblioteca / Apoios / Pistões; Externos/Embutidos; 9 itens | I4 |
| DESLIZANTES 001 | Alumínio/Madeira; 18 estilos | I5 |

## 2. O que o plugin já tem

- **Editor (004/006):**
  - janela própria com vista frontal;
  - rascunho com Desfazer/Refazer, Confirmar e Cancelar;
  - abas Estrutura, Divisão e Acabamento;
  - subvãos (`divisions.py`) e componentes externos com remover/restaurar (`structure.py`, adaptadores).
- **Frentes (003):** `adapter.set_front` (portas, duas portas, gavetas de 1 a 8, basculante, painel, vazio) e estilos por
  nome, por vão da biblioteca.
- **Folha de correr com batentes (007):** grupos FRAME/LEAF, curso livre, montante da outra folha. Base dos deslizantes.
- **Recorte não destrutivo (003):** `aggregates/perforate`. Base do painel de eletro.
- **Miniaturas:** `catalog/render_thumbnails.py` (Workbench) e `standards/previews.py` (`bpy.utils.previews`).
- **Plano de corte:** peças `CabinetPart` com `btm_component` (006).
- **Não existe:** lista de ferragens (D-14).

## 3. Alternativas avaliadas

| Alternativa | Por que não |
|---|---|
| Frentes por subvão agora | Decisão do titular (Q2c): feature seguinte; exige motor novo |
| Bays nativos de cada biblioteca para o Número de vãos | Quatro implementações diferentes; as divisões da 006 são genéricas |
| Modelar os 18 estilos de deslizante | Fora de proporção para esta feature; o estilo fica gravado |
| Aplicar fechando e reabrindo o modal | Perde a vista e a seleção; fica como alternativa se `ed.undo_push` falhar no modal |
| Uma 8ª aba "Acabamento" | O Construtor não tem; as funções vão para as abas certas (D-03) |

## 4. Referências da API (RAG 5.2), a confirmar na codificação

- `UILayout.prop_tabs_enum(icon_only=…)`, `UILayout.template_icon_view`, `bpy.utils.previews.new`
- `bpy.ops.ed.undo_push(message=…)`
- `Operator.modal` com `LEFT_ARROW`/`RIGHT_ARROW`/`UP_ARROW`/`DOWN_ARROW`
