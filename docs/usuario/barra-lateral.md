# A barra lateral do CAFFMob Draw

A aba **CAFFMob Draw** da barra lateral da Viewport 3D (tecla **N**) tem **cinco seções**, na ordem do trabalho. Cada
uma é um painel recolhível, como os do Blender. Cada função aparece num lugar só. Os caminhos rápidos ficam na própria
viewport: o menu do botão direito e o HUD.

No topo ficam sempre o ambiente atual (com o navegador de cenas), o modo de seleção da biblioteca e, se for o caso, o
aviso para ligar a cor por objeto.

## As cinco seções

| Seção | O que tem |
|---|---|
| **Construir** | **Editor de Paredes** no topo; depois Paredes, Aberturas, Piso e teto, Obstáculos, Luzes, Escadas, Imagem de referência e Geometrias (Placa e Caixa). Sem nenhuma parede, Aberturas e Piso e teto ficam desabilitados com o aviso **Desenhe uma parede primeiro** |
| **Inserir** | **Módulo Rápido**, **Importar modelo 3D**, o seletor de biblioteca (frameless, face frame, closets) com o catálogo e, abaixo, **Meus módulos**: os módulos salvos, os grupos frameless e os grupos face frame do usuário juntos, com filtro por origem |
| **Selecionado** | Só o que vale para o objeto ativo. Abre sozinha quando você seleciona algo. Para um módulo: **Medidas e cotas** (com o **Abrir editor de armário**), **Personalizar**, **Posição e vínculo** (posição, rotação, Mover Sobre, plano de inserção, elemento filho) e **Abrir**. Recolhidos: Agregados e folhas, Colisão, Arranjo, Outras e ações e, no face frame, **Opções do face frame** |
| **Verificar** | **Portas e gavetas** (abrir/fechar todas, ângulo do clique, interferência) e **Colisões** |
| **Produção/Projeto** | **Plano de corte**, **Ambientes**, **Configurações** (unidade, snap, Evitar Sobreposição, padrão de dimensões, chapa MDF), **Projeto** e, recolhido, **Desenhos 2D** (vistas de layout, detalhes, anotações), que some com a preferência **Ocultar Painéis 2D** |

O Blender lembra quais seções e grupos você deixou abertos durante a sessão. Abrir ou recolher não altera o projeto
nem entra no Ctrl+Z.

## Onde ficou cada coisa

| Antes | Agora |
|---|---|
| Aba CONSTRUTOR › Paredes & Piso, Aberturas & Vãos | **Construir** |
| Painel Room Layout (Walls, Doors & Windows, Floor & Ceiling, Obstacles, Lighting, Stairs, Reference Image) | **Construir**, nos grupos de mesmo assunto |
| Aba CONSTRUTOR › Módulo Rápido, Placa, Caixa | **Inserir** › Módulo Rápido; **Construir** › Geometrias |
| Aba CONSTRUTOR › Inspeção de Portas e Gavetas | **Verificar** › Portas e gavetas |
| Botão Mover Sobre da caixa de inspeção | **Selecionado** › Posição e vínculo, menu do botão direito e HUD |
| Aba GALERIA e painel Product Library (a mesma galeria duas vezes) | **Inserir** (uma vez) |
| "User" do frameless, biblioteca do usuário do face frame, Biblioteca de módulos | **Inserir** › **Meus módulos** |
| Importar modelo 3D (em Agregados e folhas) | **Inserir** |
| Painel Propriedades e seus subpainéis | **Selecionado** |
| Painel Face Frame Cabinet | **Selecionado** › Opções do face frame |
| Aba CONFIGURAÇÕES | **Produção/Projeto** › Configurações; os ambientes em **Produção/Projeto** › Ambientes |
| Painel Project (nome, informações, ambientes) | **Produção/Projeto** › Projeto e Ambientes |
| Aba PLANO DE CORTE e painel Plano de Corte (Nesting) | **Produção/Projeto** › Plano de corte (uma vez) |
| Painel Colisões | **Verificar** › Colisões |
| Painéis Layout Views, 2D Details e Annotations | **Produção/Projeto** › Desenhos 2D |
| "Abrir editor de paredes" em Propriedades de uma parede | **Construir** › Editor de Paredes e o menu do botão direito da parede |

## Na viewport

- **Menu do botão direito:** o submenu do objeto e as ações frequentes do tipo dele. Num módulo: Grudar (ou Desgrudar
  e Mover no plano), Mover Sobre, Abrir editor de armário, Verificar colisões, Abrir frentes e Fechar frentes. Em
  qualquer objeto: Usar como plano de inserção (e Limpar, quando houver um ativo). Parede, piso e aberturas mostram só o
  submenu deles.
- **HUD:** vem ligado em instalações novas. Para desligar, vá em **Edit › Preferences › Add-ons › CAFFMob Draw ›
  Controles na Viewport**. Ele mostra os modos (seleção, agarrar, abrir frentes, Mover Sobre) e, com um item
  selecionado, uma linha com as ações dele: Grudar, Abrir editor de armário e Verificar colisões.
- **Prévia do ímã:** ao arrastar um módulo ou uma geometria (G ou posicionamento do plugin) com o ímã ligado, a face
  plana ao alcance fica destacada e aparece o contorno de onde o item vai encostar, com **Grudar em: <objeto>**. Solte
  para grudar. **Esc** cancela e nada gruda.
