# Onboarding: Editor de armário, grudar em superfície plana e colisão

> Identificador: `004-editor-armario-grudar`
> Para quem vai testar a feature pela primeira vez, no Blender 5.2 com o plugin instalado por `python3 build.py`.

## Preparação

1. Gere e instale o pacote: `python3 build.py`, depois Edit → Preferences → Get Extensions → Install from Disk → `caffmob_draw.zip`.
2. Arquivo novo. Desenhe uma sala de 4 × 3 m com paredes de 150 mm.
3. Insira um balcão frameless de 800 mm na parede de 4 m e um aéreo na face de trás de outra parede. Para pôr o aéreo atrás, passe o cursor para o outro lado da parede durante o posicionamento.

## I1. Grudar

1. **Migração:** salve o arquivo, feche e reabra.
   - Selecione o balcão.
   - O painel de propriedades deve mostrar "Elemento filho de: <parede> — frente".
2. **Espessura:** abra o editor de paredes, mude a parede do aéreo para 200 mm e confirme.
   - O aéreo deve continuar encostado na face de trás, sem entrar na parede e sem ficar solto.
3. **Grudar num painel:**
   - Crie uma placa vertical de 18 mm (Geometria da 002) e um nicho (caixa).
   - Selecione o nicho, clique em "Grudar" e depois na lateral da placa.
   - O fundo do nicho deve encostar na lateral.
   - Gire a placa 90°: o nicho deve ir junto.
4. **G nativo:** com o nicho grudado, aperte G e arraste.
   - Ao soltar, o nicho deve estar no plano da lateral, na posição onde foi solto.
5. **Ímã:** insira um aéreo pelo catálogo e passe o cursor a uns 30 mm da lateral de um roupeiro.
   - A prévia deve encostar na lateral.
   - Em Preferences → Add-ons → CAFFMob Draw, desligue "Ímã": o mesmo gesto não deve mais encostar.
   - Mude a distância para 20 mm e teste de novo.
6. **Fora da face:** encurte a placa até o nicho ficar fora dela.
   - A barra de status deve avisar "Item fora da face: Nicho" e o nicho deve ficar no lugar.
7. **Apagar o hospedeiro:** apague a placa (X).
   - O nicho deve ficar no mesmo lugar, sem vínculo, com o aviso "Vínculo perdido: Nicho".
8. **Desgrudar:** grude de novo, clique em "Desgrudar" e mova o hospedeiro.
   - O item não deve se mover.

## I2. Colisão

1. Arraste o balcão 20 mm para dentro da parede e clique em "Verificar colisões".
   - Deve aparecer "Penetração em parede, 20 mm" com o balcão e a parede.
2. Clique em "Ir para": os dois devem ficar selecionados e enquadrados.
3. Encoste dois balcões lado a lado e verifique: não deve aparecer nenhuma ocorrência.
4. Mova qualquer item: o painel deve mudar para "Desatualizado".
5. No item, mude "Colisão" para "Desativada" e verifique de novo: as ocorrências dele devem sumir.
6. Com duas colisões pendentes e o resultado em dia, salve o arquivo.
   - O arquivo deve ser gravado e a barra de status deve dizer "2 colisões pendentes".
7. Insira um aéreo pelo catálogo sobre outro aéreo.
   - Ao soltar, o aéreo deve ficar onde foi solto, com o destaque e "Colide com <outro>".
8. (Could) "Afastar até encostar" deve tirar o balcão de dentro da parede, e um Ctrl+Z deve devolvê-lo.

## I3. Editor de armário

1. Selecione um roupeiro (closets) e clique em "Abrir editor de armário".
   - Deve abrir uma janela com a vista frontal e a lista de componentes.
2. Clique na gaveta 2 na vista: a lista deve destacar "Gaveta 2". Faça o inverso pela lista.
3. Mude a largura e confira:
   - a vista deve atualizar;
   - "Ajustes automáticos" deve listar as frentes redistribuídas.
4. Digite uma largura abaixo do mínimo:
   - o campo deve mostrar `DIM-003` com a faixa;
   - Confirmar deve ficar indisponível.
5. Troque um vão por 3 gavetas e aperte Ctrl+Z duas vezes:
   - o rascunho deve voltar;
   - o histórico da cena não deve mudar.
6. Clique em Cancelar e escolha descartar: o roupeiro deve ficar igual a antes de abrir o editor.
7. Abra de novo, faça uma edição e clique em Confirmar.
   - Um Ctrl+Z na cena deve devolver o roupeiro anterior inteiro.
8. Repita os passos 1, 6 e 7 com um balcão frameless, um face frame e um módulo `btm`.

## Comandos de verificação

```bash
ruff check caffmob_draw/
python3 docs/rag/tools/check_api.py
python3 -m unittest discover -s tests -p 'test_*.py'
blender --background --factory-startup --python-exit-code 1 --python tests/blender_004_stick_smoke.py
blender --background --factory-startup --python-exit-code 1 --python tests/blender_004_collision_smoke.py
blender --python-exit-code 1 --python tests/blender_004_cabinet_editor_smoke.py   # precisa de janela
```
