# Design brief: editor de armário em abas (T025, `/impeccable shape`)

> Data: 2026-10-08. Registro: interface de ferramenta (Operate).
> Superfície: barra lateral do editor de armário (Image Editor › região UI › categoria "Editor de Armário"), Blender 5.2.
> Decisões do titular nesta passada: remover abre uma janela com os 3 modos; a terceira aba se chama **Acabamento**.

## 1. Público e trabalho

Quem usa é o projetista com um armário aberto no editor e a vista frontal ao lado. Ele quer mudar a caixa (tirar
uma lateral, engrossar o tampo) e dividir o interior, conferir na vista e confirmar. Sucesso: fazer qualquer uma
dessas coisas sem rolar a barra e sem procurar onde está.

## 2. Direção

- **Mundo visual = o tema do Blender.** Só controles nativos do `UILayout`: abas (`prop_tabs_enum`), `box`, `row`,
  `column`, campos, ícones nativos e `alert`. Nenhuma cor própria na barra; a cor de estado fica na vista frontal
  (subvão escolhido em destaque, removida tracejada).
- **Tese:** "uma aba por trabalho, o rodapé é o contrato". As abas mudam o que se edita. O rodapé (mensagens,
  desfazer, Confirmar/Cancelar) é igual em todas e nunca some.
- **Momento focal:** na aba Divisão, o vão escolhido aparece **em texto** no painel e **destacado** na vista; o botão
  Adicionar diz onde a chapa vai entrar.

## 3. Estrutura do painel (de cima para baixo)

**Cabeçalho (sempre).** Linha 1: nome do módulo e biblioteca. Linha 2: estado do rascunho ("Sem alterações" /
"Rascunho alterado"). Linha 3: abas **Estrutura · Divisão · Acabamento**, com ícone e texto.

**Aba Estrutura**
1. *Medidas*: Largura, Altura e Profundidade num bloco alinhado. Abaixo, uma linha apagada com as três faixas
   permitidas. O campo com erro fica em `alert`.
2. *Componentes*: uma linha por chapa que o módulo tem (máximo 5, sem lista rolável):
   `nome · medidas · material espessura · [✎] [✕]`.
   - Alterada: "MDP 18 mm · alterado".
   - Removida: nome apagado, "removido · <modo>" e um só botão **Restaurar**.
   - Ação que a biblioteca não faz: botão desabilitado, motivo no tooltip.
   - Face frame: aviso fixo "Face frame ainda não entra no plano de corte".
3. **✕ abre a janela "Remover <chapa>"** com os três modos em lista de opções. Manter tudo vem marcado. Cada modo que
   a biblioteca não faz fica apagado com o motivo na linha de baixo. Botão "Remover".
4. **✎ abre a janela "<chapa>"** com Espessura (0 = do Configurador) e Material da chapa (Do Configurador, MDF,
   MDP…).

**Aba Divisão**
1. Linha de informação: "Chapa: MDP 15 mm (Configurador › <linha>)". No face frame, o mesmo aviso da Estrutura.
2. *Nova divisão*:
   - **Vão** (lista) e a dica "ou clique no vão na vista";
   - **Orientação** com dois botões, Vertical e Horizontal, com ícone;
   - **Recuo na frente** e **Recuo atrás**: cada um com uma caixa de marcar e o valor ao lado, que fica apagado quando
     desmarcado (padrão 20 mm);
   - botão grande **Adicionar** ("Adicionar em <vão>").
3. *Divisões*: uma linha por chapa, `nome · detalhe (orientação, posição, recuos, material) · [✎] [✕]`. Linha com
   erro em `alert`. Lista vazia: "Nenhuma divisão. Escolha um vão e clique em Adicionar."

**Aba Acabamento.** A lista de componentes da 004 (selecionar na lista ou na vista) e as seções Frentes, Puxadores,
Materiais e Divisões internas da 003, sem mudança de conteúdo.

**Rodapé (todas as abas)**
- Mensagens: "Sem erros nem avisos" ou as mensagens com ícone de gravidade. Sempre em texto.
- Ajustes automáticos: recolhido.
- Desfazer e Refazer.
- **Confirmar** (maior) e Cancelar; Fechar e Salvar como módulo.

## 4. Estados e faixas

- Componentes: de 0 a 5 linhas. Divisões: de 0 a 20.
- Um vão: já vem escolhido. Nenhum vão: a lista mostra "Sem vão interno" e Adicionar fica desabilitado.
- Erro de divisão (`DIV-*`) ou de espessura (`STR-002`): a linha em `alert`, a mensagem no rodapé e Confirmar
  bloqueado.

## 5. Restrições

- Português com inglês (abas "Structure · Divisions · Finish").
- Nenhum `bpy.props` novo além do data-delta.
- Estado em texto, além da cor (PRODUCT.md).
- Fora do escopo: reorganizar o conteúdo da aba Acabamento.
