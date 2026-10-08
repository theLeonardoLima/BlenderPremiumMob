# Product

<!-- impeccable:product-schema 1 -->

## Platform

desktop — extensão do Blender 5.2 (fora dos valores `web`/`ios`/`android`/`adaptive` do esquema: a interface é a do
próprio Blender, não uma página nem um app móvel)

## Users

Projetista de móveis planejados de loja ou marcenaria. Desenha o ambiente do cliente (paredes, aberturas, piso), insere
e personaliza os módulos, confere encaixes e colisões, apresenta o projeto e entrega à fábrica a lista de peças e o plano
de corte. É o mesmo trabalho que hoje se faz no Promob.

## Product Purpose

Projetar ambientes de interiores e marcenaria paramétrica dentro do Blender e gerar a produção a partir do projeto: lista
de peças, plano de corte otimizado em chapas de MDF e o JSON de produção. Sucesso: o projetista vai do ambiente vazio ao
plano de corte sem sair do Blender e sem retrabalho.

## Positioning

- Fluxo de projeto "estilo Promob" **gratuito e aberto** (GPL-3.0).
- Roda **dentro do Blender**: modelagem, materiais e renderização nativos no mesmo arquivo do projeto.
- **Do projeto à produção**: o ambiente 3D gera a lista de peças, o plano de corte e o JSON de produção.
- **Paramétrico e personalizável**: módulos paramétricos de quatro bibliotecas (frameless, face frame, closets e os
  módulos do próprio CAFFMob Draw), personalização por instância, agregados de modelos externos e biblioteca do usuário.
- **Conexão com a conta CAFF DIGITAL** para obter novos blocos e texturas. *Confirmado como posicionamento; ainda não
  implementado (não há código dessa integração no repositório).*

## Operating Context

- Blender 5.2, Viewport 3D com a barra lateral (N), aba **CAFFMob Draw**; janelas 2D próprias para o Editor de
  Paredes e o Editor de Armário.
- Fluxo típico: desenhar paredes → aberturas → inserir módulos pela galeria → personalizar, grudar e reposicionar →
  verificar frentes e colisões → plano de corte e exportação.
- Unidades em mm; chapa padrão 2750 × 1830 mm.

## Capabilities and Constraints

- Paredes (editor 2D), piso e teto, portas e janelas, obstáculos.
- Módulos paramétricos com personalização, Editor de Armário, agregados e folhas de porta, grudar em superfícies
  planas (elemento filho), Mover Sobre, colisão de corpo e interferência de frentes.
- Lista de peças, plano de corte (nesting) e JSON de produção.
- Código é um fork do Home Builder 5: convivem painéis legados (`HOME_BUILDER_PT_*`) e a camada nova (`BTM_*`). Isso
  gera duplicação na barra lateral, alvo da reorganização planejada.
- **Em aberto**: escopo e forma da integração com a conta CAFF DIGITAL (autenticação, catálogo, download de blocos e
  texturas).

## Brand Commitments

- Nome: **CAFFMob Draw**.
- Interface em **português do Brasil primeiro**, com tradução completa para **inglês (EUA)** (`caffmob_draw/data/
  translations/`).

## Evidence on Hand

- Guias do usuário em `docs/usuario/`.
- Especificações e features em `_reversa_sdd/` e `_reversa_forward/`.
- Não há depoimentos, clientes, números de uso ou preços registrados; nada disso deve ser inventado.

## Product Principles

1. **A viewport é o lugar principal.** Manipular direto no 3D (arrastar, grudar, cotas, destaques); a barra lateral
   apoia, não lidera.
2. **Convenções do Blender.** Painéis na barra lateral, menus de contexto, operadores com desfazer, atalhos e o tema do
   Blender; nenhuma interface inventada fora desse padrão.
3. **Cada função num lugar só.** Sem botões ou galerias repetidos; caminhos de contexto (menu do botão direito, HUD)
   complementam, não duplicam painéis.
4. **Contextual ao selecionado.** Mostrar o que vale para o que está selecionado; o resto fica recolhido.
5. **Do projeto à produção sem retrabalho.** Toda mudança no projeto se reflete na produção, e o que ficou
   desatualizado é avisado.

## Accessibility & Inclusion

Estados (erro, colisão, desatualizado, item grudado) sempre em texto, além da cor.
