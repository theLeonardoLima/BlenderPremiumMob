# Dependências do Projeto — BlenderToMob

Este documento apresenta a análise de dependências e requisitos de compatibilidade do projeto **BlenderToMob**, coletados na fase de Reconhecimento.

## 1. Requisitos do Sistema e Ambiente de Execução

* **Plataforma Target:** Blender 3D (versão mínima **4.2.0**)
* **Linguagem Principal:** Python 3 (embutido no interpretador do Blender)
* **Gerenciador de Pacotes:** Sistema de Extensões do Blender (nova API introduzida na versão 4.2.0)

## 2. Dependências de Código (Imports)

O add-on utiliza bibliotecas integradas e módulos específicos do ecossistema Blender. Não há dependências externas do pip declaradas.

### 2.1 Módulos Internos do Blender (bpy API)
* `bpy` — Interface de dados principal do Blender (criação de objetos, coleções, cenas e propriedades).
* `bmesh` — Módulo para manipulação de malhas poligonais de baixo nível em alta performance (geração paramétrica de paredes, pisos e armários).
* `gpu` — Renderização de overlays customizados na viewport (linhas e formas 3D usando shaders nativos do Blender).
* `gpu_extras.batch` — Utilitários para criação de lotes de dados geométricos para renderização rápida por GPU.
* `blf` — Módulo de renderização de texto e fontes bidimensionais na viewport.
* `mathutils` — Classes para manipulação matemática de vetores (`Vector`), matrizes de transformação (`Matrix`) e ângulos (`Euler`).
* `bpy_extras.view3d_utils` — Utilitários de projeção e raycast (conversão de coordenadas de tela 2D para mundo 3D).

### 2.2 Módulos Standard do Python (Built-ins)
* `math` — Operações e funções trigonométricas.
* `os` — Operações de sistema de arquivos (utilizado pelo script de build).
* `zipfile` — Compactação e empacotamento (utilizado pelo script de build para gerar a extensão `.zip`).
* `json` — Serialização e armazenamento estruturado (utilizado para salvar os segmentos de paredes poligonais como propriedade customizada).

## 3. Licenciamento e Tags

Conforme especificado no manifesto `blender_manifest.toml`:
* **Licença:** `SPDX:GPL-3.0-or-later` (Gnu General Public License v3 ou posterior, obrigatória para integração profunda com a GPL do Blender).
* **Tags do Projeto:** `Design`, `Parametric`, `CAD`, `Woodworking`, `Furniture`
