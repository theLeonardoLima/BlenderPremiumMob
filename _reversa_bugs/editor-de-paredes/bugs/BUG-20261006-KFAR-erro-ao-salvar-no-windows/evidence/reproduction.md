# Cápsula de reprodução — BUG-20261006-KFAR

- Base: clone limpo de `git@github.com:theLeonardoLima/BlenderPremiumMob.git`, branch `master`, commit `b92ac2e`
  (o branch padrão do GitHub é o `main`, antigo: `4b87c21`, ainda com o pacote `blendertomob`)
- Ambiente: Linux 6.8, Blender 5.2, pasta de usuário temporária (`BLENDER_USER_RESOURCES`)
- Passos (o mesmo caminho do titular no Windows: clone + `build.py`):
  1. `git clone ... && git checkout master && python3 build.py` → `caffmob_draw.zip`
  2. `blender --command extension install-file -r user_default -e caffmob_draw.zip`
  3. `blender --background --factory-startup --python evidence/reproducao-clone-limpo.py` (aplica uma sala 10 x 20 m pelo editor)
- Resultado: `OSError load: .../caffmob_draw/geometry_nodes/GeoNodeWall.blend failed to open blend file` (o mesmo do print)
- Taxa: 1/1 · Classificação: **deterministic** (independe do Windows: depende de montar o pacote a partir do git)

Contagem: o pacote local tem 107 `.blend` (26,2 MB); o zip gerado do clone tem **0**
(`evidence/blends-ausentes-no-clone.txt`). Os 107 são idênticos (sha1) aos da cópia antiga na raiz, que é a única
versionada. Causa: `.gitignore` tem `*.blend`.
