# Onboarding: Barra lateral em 5 seções

> Para quem vai testar pela primeira vez, no Blender 5.2 com o plugin instalado por `python3 build.py`.

## Preparação

1. Instale o `caffmob_draw.zip` gerado.
2. Abra um arquivo novo. Desenhe uma sala com o Editor de Paredes, insira um balcão frameless, um roupeiro (closets) e
   um módulo face frame.

## I2. Navegação única

1. Abra a aba **CAFFMob Draw** (tecla N). Devem aparecer só 5 painéis: **Construir**, **Inserir**, **Selecionado**,
   **Verificar** e **Produção/Projeto**.
2. **Arquivo novo, sem paredes:** em Construir, Aberturas e Piso e teto devem estar desabilitados, com a linha
   "Desenhe uma parede primeiro".
3. **Inserir:**
   - a galeria deve aparecer uma vez só, com o seletor de biblioteca;
   - em **Meus módulos**, salve um módulo (003) e confira que ele aparece junto com os grupos do frameless e do face
     frame, com a origem de cada um.
4. **Selecionado:**
   - recolha Selecionado e clique num balcão na viewport: Selecionado deve se abrir sozinho;
   - devem aparecer no máximo 4 grupos abertos;
   - no face frame, deve aparecer também "Opções do face frame" recolhido, e não pode existir um painel "Face Frame
     Cabinet" separado.
5. **Verificar:** abrir/fechar frentes, interferência e colisões devem aparecer juntos.
6. **Produção/Projeto:**
   - o plano de corte e os ambientes devem aparecer uma vez cada;
   - "Evitar Sobreposição" fica nas configurações;
   - "Desenhos 2D" fica recolhido e some ao ligar "Ocultar Painéis 2D" nas preferências.

## I3. Viewport

1. **Botão direito num balcão:** devem aparecer o submenu do módulo, Grudar, Mover no plano, Mover Sobre, Abrir editor
   de armário, Verificar colisões e Abrir/Fechar frentes. Numa parede, só as ações da parede.
2. **HUD:**
   - num perfil novo, o HUD deve aparecer no topo da viewport;
   - com o balcão selecionado, deve aparecer uma linha com até 4 ações dele;
   - desligue em Preferências › CAFFMob Draw › Controles na Viewport: o HUD some.
3. **Prévia do ímã:**
   - com o ímã ligado, arraste (G) um aéreo solto até perto da lateral do roupeiro;
   - a lateral deve ficar destacada, com o contorno do aéreo encostado e o nome do roupeiro;
   - solte: o aéreo deve ficar grudado ali;
   - repita e aperte Esc: a prévia some e nada gruda.

## Comandos de verificação

```bash
ruff check caffmob_draw/
python3 docs/rag/tools/check_api.py
python3 -m unittest discover -s tests -p 'test_*.py'
blender --background --factory-startup --python-exit-code 1 --python tests/blender_005_sidebar_inventory.py
blender --factory-startup --enable-event-simulate --python tests/blender_005_viewport_smoke.py   # precisa de janela
```
