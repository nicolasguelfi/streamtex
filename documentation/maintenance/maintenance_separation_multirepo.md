# Plan de Maintenance : Séparation Multi-Repo & Déploiement Indépendant

> **Date** : 2026-02-25
> **Auteur** : Claude Code (assisté par Nicolas Guelfi)
> **Version** : 1.0
> **Statut** : Planification

---

## Table des matières

1. [Résumé exécutif](#1-résumé-exécutif)
2. [État actuel](#2-état-actuel)
3. [Architecture cible](#3-architecture-cible)
4. [Phase 1 — Publication de la librairie sur PyPI](#4-phase-1--publication-de-la-librairie-sur-pypi)
5. [Phase 2 — Séparation du repo Manuals](#5-phase-2--séparation-du-repo-manuals)
6. [Phase 3 — Indépendance des projets utilisateur](#6-phase-3--indépendance-des-projets-utilisateur)
7. [Phase 4 — Renommage des services Render](#7-phase-4--renommage-des-services-render)
8. [Matrice des risques](#8-matrice-des-risques)
9. [Calendrier recommandé](#9-calendrier-recommandé)
10. [Annexe A — Migration vers un domaine personnalisé](#annexe-a--migration-vers-un-domaine-personnalisé)
11. [Annexe B — Migration vers une organisation GitHub](#annexe-b--migration-vers-une-organisation-github)
12. [Annexe C — Architecture shared-blocks en multi-repo](#annexe-c--architecture-shared-blocks-en-multi-repo)
13. [Annexe D — Checklist de validation par phase](#annexe-d--checklist-de-validation-par-phase)

---

## 1. Résumé exécutif

### Objectif

Séparer le monorepo StreamTeX actuel en plusieurs dépôts indépendants pour :

- **Publier la librairie `streamtex` sur PyPI** (installation standard via `pip install streamtex`)
- **Déployer chaque projet indépendamment** sur Render.com
- **Maintenir la librairie séparément** des projets utilisateur
- **Adopter une convention de nommage cohérente** pour les URLs de déploiement

### Décisions prises

| Aspect | Décision |
|--------|----------|
| **Package Python** | PyPI public (`pip install streamtex`) |
| **Stratégie repos** | Multi-repo (librairie + manuals + projets séparés) |
| **Compte GitHub** | `nicolasguelfi` (personnel), migration organisation en annexe |
| **URLs Render** | Convention `{projet}-streamtex.onrender.com` (domaine perso en annexe) |
| **Projet prioritaire** | AI4SE déployé en premier indépendamment |
| **Nom PyPI** | `streamtex` — **disponible** (vérifié le 2026-02-25) |

### Architecture cible (vue d'ensemble)

```
AVANT (monorepo unique)                    APRÈS (multi-repo)
─────────────────────────                  ───────────────────
nicolasguelfi/streamtex                    nicolasguelfi/streamtex
├── streamtex/          ─────────────►       └── streamtex/        (librairie seule, PyPI)
├── documentation/
│   └── manuals/        ─────────────►     nicolasguelfi/streamtex-manuals
│       ├── stx_manual_intro/                ├── stx_manual_intro/
│       ├── stx_manual_advanced/             ├── stx_manual_advanced/
│       ├── stx_manual_deploy/               ├── stx_manual_deploy/
│       ├── stx_manuals_collection/          ├── stx_manuals_collection/
│       └── stx_manuals_shared-blocks/       └── shared-blocks/
├── projects/
│   ├── AI4SE/          ─────────────►     nicolasguelfi/ai4se-streamtex
│   ├── project_aiai18h/  (plus tard)        └── (standalone project)
│   └── ...
├── tests/              ─────────────►     (dans nicolasguelfi/streamtex)
└── deploy/             ─────────────►     (réparti dans chaque repo)
```

---

## 2. État actuel

### 2.1 Structure monorepo

```
nicolasguelfi/streamtex (branche main)
├── streamtex/                    # Librairie Python (package source)
├── projects/                     # Projets utilisateur
│   ├── AI4SE/                    #   Cours AI4SE (prioritaire)
│   ├── project_aiai18h/          #   Cours AIAI18H
│   ├── modelsward/               #   Conférence Modelsward
│   ├── project_modelsward/       #   (doublon Modelsward)
│   ├── project_html_example/     #   Exemple migration HTML
│   └── convert_html_to_streamtex/  # Outil de conversion
├── documentation/
│   ├── manuals/
│   │   ├── stx_manual_intro/     # Manuel d'introduction
│   │   ├── stx_manual_advanced/  # Manuel avancé
│   │   ├── stx_manual_deploy/    # Manuel déploiement
│   │   ├── stx_manuals_collection/ # Hub collection
│   │   └── stx_manuals_shared-blocks/ # Blocs partagés manuels
│   ├── coding_standards.md
│   ├── streamtex_cheatsheet_*.md
│   ├── template_project/
│   ├── template_collection/
│   └── maintenance/
├── tests/                        # 203 tests unitaires
├── deploy/                       # Scripts déploiement multi-cibles
├── .github/workflows/ci.yml      # CI/CD
├── Dockerfile                    # Image Docker universelle
├── docker-compose.yml            # Dev local (3 services)
├── render.yaml                   # Render.com (4 services)
├── pyproject.toml                # Config package (v0.2.0)
└── CLAUDE.md                     # Instructions Claude Code
```

### 2.2 Déploiement Render actuel

| Service Render | Dossier source | URL actuelle |
|----------------|---------------|--------------|
| `streamtex` | `documentation/manuals/stx_manuals_collection` | `streamtex.onrender.com` |
| `streamtex-intro` | `documentation/manuals/stx_manual_intro` | `streamtex-intro.onrender.com` |
| `streamtex-advanced` | `documentation/manuals/stx_manual_advanced` | `streamtex-advanced.onrender.com` |
| `streamtex-deploy` | `documentation/manuals/stx_manual_deploy` | `streamtex-deploy.onrender.com` |

**Limitations actuelles** :
- Tous les services pointent vers le **même repo** GitHub
- La librairie `streamtex/` est **copiée dans chaque conteneur Docker** (pas installée via pip)
- Les projets importent la librairie via **manipulation de `sys.path`**
- Les 4 services consomment le **quota gratuit partagé** (750h/mois)
- Un push sur `main` rebuild **tous** les services (malgré les `buildFilter`)

### 2.3 Comment les projets utilisent la librairie aujourd'hui

```python
# Pattern actuel dans setup.py de chaque projet
try:
    import streamtex
except ImportError:
    import os, sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
```

Ce pattern fragile sera remplacé par un simple `pip install streamtex`.

---

## 3. Architecture cible

### 3.1 Repos GitHub

| Repo | Contenu | PyPI | Render |
|------|---------|------|--------|
| `nicolasguelfi/streamtex` | Librairie seule + tests + docs API | `streamtex` | Non (pas de service web) |
| `nicolasguelfi/streamtex-manuals` | Manuels + collection hub + shared-blocks | — | 4 services |
| `nicolasguelfi/ai4se-streamtex` | Projet AI4SE | — | 1 service |
| *(futur)* `nicolasguelfi/aiai18h-streamtex` | Projet AIAI18H | — | 1 service |

### 3.2 Convention de nommage des services Render

**Formule** : `{identifiant}-streamtex`

| Service | Nom Render | URL |
|---------|-----------|-----|
| Hub collection | `streamtex` | `streamtex.onrender.com` |
| Manuel intro | `intro-manual-streamtex` | `intro-manual-streamtex.onrender.com` |
| Manuel avancé | `advanced-manual-streamtex` | `advanced-manual-streamtex.onrender.com` |
| Manuel deploy | `deploy-manual-streamtex` | `deploy-manual-streamtex.onrender.com` |
| Projet AI4SE | `ai4se-streamtex` | `ai4se-streamtex.onrender.com` |

### 3.3 Flux de dépendances

```
                    ┌─────────────────┐
                    │   PyPI          │
                    │   streamtex     │
                    │   v0.3.0        │
                    └────────┬────────┘
                             │  pip install streamtex
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
     ┌────────────┐  ┌────────────┐  ┌────────────┐
     │ streamtex- │  │ ai4se-     │  │ aiai18h-   │
     │ manuals    │  │ streamtex  │  │ streamtex  │
     └────────────┘  └────────────┘  └────────────┘
           │
     ┌─────┴─────────┬──────────┬──────────┐
     ▼               ▼          ▼          ▼
   intro          advanced   deploy    collection
   manual         manual     manual    hub
```

---

## 4. Phase 1 — Publication de la librairie sur PyPI

### 4.1 Objectif

Publier `streamtex` comme package Python standard, installable via `pip install streamtex`.

### 4.2 Pré-requis

- [ ] Compte PyPI créé sur [pypi.org](https://pypi.org)
- [ ] Compte Test PyPI créé sur [test.pypi.org](https://test.pypi.org) (pour les tests)
- [ ] Token API PyPI généré
- [ ] `twine` et `build` installés (`uv add --group dev build twine`)

### 4.3 Étapes détaillées

#### 4.3.1 Préparer le pyproject.toml pour la publication

Le `pyproject.toml` actuel doit être enrichi :

```toml
[project]
name = "streamtex"
version = "0.3.0"  # Bump pour la première release publique
description = "A Streamlit-based document rendering library with CSS Grid, styles, and book navigation"
readme = "README.md"
license = {text = "MIT"}
requires-python = ">=3.10"
authors = [
    {name = "Nicolas Guelfi", email = "nicolas.guelfi@laposte.net"}
]
keywords = ["streamlit", "presentation", "documents", "css-grid", "rendering"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Framework :: Streamlit",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Topic :: Text Processing :: Markup",
]

[project.urls]
Homepage = "https://github.com/nicolasguelfi/streamtex"
Documentation = "https://streamtex.onrender.com"
Repository = "https://github.com/nicolasguelfi/streamtex"
Issues = "https://github.com/nicolasguelfi/streamtex/issues"

[build-system]
requires = ["setuptools>=68.0", "setuptools-scm>=8.0"]
build-backend = "setuptools.build_meta"

[tool.setuptools.packages.find]
include = ["streamtex*"]

[tool.setuptools.package-data]
"streamtex.static" = ["*.css"]
```

#### 4.3.2 Créer un README.md orienté utilisateur

Le README actuel du monorepo doit être remplacé par un README orienté "installateur" :

```markdown
# StreamTeX

A Streamlit-based document rendering library with CSS Grid layouts,
composable styles, and paginated book navigation.

## Installation

pip install streamtex

## Quick Start

import streamtex as sx
from streamtex.styles.core import Style

style = Style("color: navy; font-size: 1.2em;", "my-style")
sx.st_write(style, "Hello StreamTeX!")

## Documentation

### Online manuals (read & explore)

- [All manuals (hub)](https://streamtex.onrender.com)
- [Introduction](https://intro-manual-streamtex.onrender.com)
- [Advanced](https://advanced-manual-streamtex.onrender.com)
- [Deployment Guide](https://deploy-manual-streamtex.onrender.com)

### Examples (source code)

The manuals are also available as source code — clone and run them locally
to study the examples:

git clone https://github.com/nicolasguelfi/streamtex-manuals
cd streamtex-manuals
uv sync
uv run streamlit run stx_manual_intro/book.py

See [streamtex-manuals](https://github.com/nicolasguelfi/streamtex-manuals)
for the full list of example projects.
```

#### 4.3.3 Nettoyer le repo pour ne garder que la librairie

**Fichiers à garder dans `nicolasguelfi/streamtex`** :

```
streamtex/                  # Package source
tests/                      # Tests unitaires
documentation/
├── coding_standards.md     # Standards (utile pour contributeurs)
├── streamtex_cheatsheet_en.md
├── streamtex_cheatsheet_fr.md
├── template_project/       # Template starter (utile pour utilisateurs)
└── template_collection/    # Template collection
pyproject.toml
uv.lock
README.md
LICENSE
CLAUDE.md
.github/workflows/ci.yml   # Tests + publication PyPI
.gitignore
```

**Fichiers à déplacer** (vers d'autres repos) :

```
projects/                   → repos individuels
documentation/manuals/      → nicolasguelfi/streamtex-manuals
deploy/                     → réparti (scripts génériques restent, spécifiques migrent)
Dockerfile                  → simplifié (pour tests/CI uniquement)
docker-compose.yml          → supprimé (ou simplifié)
render.yaml                 → supprimé (pas de service web pour la lib)
run-test-projects.sh        → vers streamtex-manuals
```

#### 4.3.4 Ajouter un workflow CI/CD pour la publication PyPI

```yaml
# .github/workflows/publish.yml
name: Publish to PyPI

on:
  release:
    types: [published]

permissions:
  id-token: write  # Pour trusted publishing (OIDC)

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
      - run: uv sync --frozen
      - run: uv run ruff check streamtex/
      - run: uv run pytest tests/ -v

  publish:
    needs: test
    runs-on: ubuntu-latest
    environment: pypi  # Protection environment sur GitHub
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
      - run: uv build
      - uses: pypa/gh-action-pypi-publish@release/v1
        # Trusted publishing via OIDC — pas besoin de token !
```

#### 4.3.5 Configurer le Trusted Publishing sur PyPI

1. Aller sur [pypi.org](https://pypi.org) → Account Settings → Publishing
2. Ajouter un "Trusted Publisher" :
   - **Owner** : `nicolasguelfi`
   - **Repository** : `streamtex`
   - **Workflow** : `publish.yml`
   - **Environment** : `pypi`
3. Sur GitHub → Settings → Environments → Créer `pypi`

#### 4.3.6 Première publication (test puis production)

```bash
# 1. Build local pour vérifier
uv build
# Vérifie que dist/ contient streamtex-0.3.0.tar.gz et streamtex-0.3.0-py3-none-any.whl

# 2. Test sur TestPyPI d'abord
uv run twine upload --repository testpypi dist/*
# Vérifier sur https://test.pypi.org/project/streamtex/

# 3. Tester l'installation depuis TestPyPI
pip install --index-url https://test.pypi.org/simple/ streamtex

# 4. Publication production (via GitHub Release)
# Créer une release sur GitHub → le workflow publish.yml s'exécute automatiquement
```

### 4.4 Versioning

Adopter le **Semantic Versioning** :

| Version | Signification |
|---------|--------------|
| `0.3.0` | Première release PyPI (breaking: `sys.path` → pip) |
| `0.3.x` | Correctifs et petites améliorations |
| `0.4.0` | Nouvelles fonctionnalités (non-breaking) |
| `1.0.0` | API stable, contrat de compatibilité |

**Politique de versions** :
- Bumper la version dans `pyproject.toml` avant chaque release
- Créer un tag Git : `git tag v0.3.0`
- Créer une GitHub Release à partir du tag → déclenche la publication PyPI

---

## 5. Phase 2 — Séparation du repo Manuals

### 5.1 Objectif

Créer un repo dédié `nicolasguelfi/streamtex-manuals` contenant les manuels et leur infrastructure de déploiement.

### 5.2 Stratégie d'accès aux manuels pour les utilisateurs

Les manuels ne sont **pas inclus dans le package PyPI** (trop lourd, hors périmètre d'une librairie). À la place, les utilisateurs y accèdent de deux manières complémentaires :

| Besoin | Solution | URL |
|--------|----------|-----|
| **Lire la documentation** | Hub collection déployé sur Render | `streamtex.onrender.com` |
| **Étudier/copier les exemples** | Cloner le repo GitHub | `github.com/nicolasguelfi/streamtex-manuals` |
| **Trouver les liens** | README du package PyPI | `pypi.org/project/streamtex` |

Le README sur PyPI (section 4.3.2) pointe vers les deux ressources : manuels en ligne et repo des exemples.

### 5.2 Structure du repo streamtex-manuals

```
nicolasguelfi/streamtex-manuals
├── stx_manual_intro/
│   ├── book.py
│   ├── blocks/
│   ├── custom/
│   ├── static/
│   └── .streamlit/config.toml
├── stx_manual_advanced/
│   ├── book.py
│   ├── blocks/
│   ├── custom/
│   ├── static/
│   └── .streamlit/config.toml
├── stx_manual_deploy/
│   ├── book.py
│   ├── blocks/
│   ├── custom/
│   ├── static/
│   └── .streamlit/config.toml
├── stx_manuals_collection/
│   ├── book.py
│   ├── collection.toml
│   ├── blocks/
│   ├── custom/
│   └── .streamlit/config.toml
├── shared-blocks/
│   ├── blocks/
│   ├── custom/
│   └── static/
├── Dockerfile
├── docker-compose.yml
├── render.yaml
├── pyproject.toml              # Dépendance: streamtex>=0.3.0
├── uv.lock
├── run-projects.sh
└── README.md
```

### 5.3 Modifications clés

#### 5.3.1 Nouveau pyproject.toml (manuals)

```toml
[project]
name = "streamtex-manuals"
version = "1.0.0"
requires-python = ">=3.10"
dependencies = [
    "streamtex>=0.3.0",        # ← Installé depuis PyPI !
    "streamlit>=1.54.0",
]

[build-system]
requires = ["setuptools>=68.0"]
build-backend = "setuptools.build_meta"
```

#### 5.3.2 Nouveau Dockerfile (manuals)

```dockerfile
FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app
ENV UV_LINK_MODE=copy

# Dépendances (streamtex vient de PyPI maintenant)
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

# Copie du projet cible
ARG FOLDER=stx_manual_intro
COPY ${FOLDER}/ ./${FOLDER}/
COPY shared-blocks/ ./shared-blocks/

WORKDIR /app/${FOLDER}

EXPOSE 8501
HEALTHCHECK CMD curl -f http://localhost:8501/_stcore/health
CMD ["uv", "run", "streamlit", "run", "book.py", \
     "--server.port=8501", "--server.address=0.0.0.0", \
     "--server.headless=true"]
```

**Changement majeur** : Plus besoin de copier `streamtex/` dans le conteneur — la librairie est installée via `uv sync` depuis PyPI.

#### 5.3.3 Nouveau render.yaml (manuals)

```yaml
services:
  - type: web
    name: streamtex
    runtime: docker
    repo: https://github.com/nicolasguelfi/streamtex-manuals
    branch: main
    plan: free
    dockerfilePath: ./Dockerfile
    dockerContext: .
    envVars:
      - key: FOLDER
        value: stx_manuals_collection
      - key: STX_URL_TEST_INTRO
        value: https://intro-manual-streamtex.onrender.com
      - key: STX_URL_TEST_ADVANCED
        value: https://advanced-manual-streamtex.onrender.com
      - key: STX_URL_TEST_DEPLOY
        value: https://deploy-manual-streamtex.onrender.com
      - key: STX_PASSWORD
        value: stx
    healthCheckPath: /_stcore/health

  - type: web
    name: intro-manual-streamtex
    runtime: docker
    repo: https://github.com/nicolasguelfi/streamtex-manuals
    branch: main
    plan: free
    dockerfilePath: ./Dockerfile
    dockerContext: .
    envVars:
      - key: FOLDER
        value: stx_manual_intro
      - key: STX_PASSWORD
        value: stx
    healthCheckPath: /_stcore/health

  - type: web
    name: advanced-manual-streamtex
    runtime: docker
    repo: https://github.com/nicolasguelfi/streamtex-manuals
    branch: main
    plan: free
    dockerfilePath: ./Dockerfile
    dockerContext: .
    envVars:
      - key: FOLDER
        value: stx_manual_advanced
      - key: STX_PASSWORD
        value: stx
    healthCheckPath: /_stcore/health

  - type: web
    name: deploy-manual-streamtex
    runtime: docker
    repo: https://github.com/nicolasguelfi/streamtex-manuals
    branch: main
    plan: free
    dockerfilePath: ./Dockerfile
    dockerContext: .
    envVars:
      - key: FOLDER
        value: stx_manual_deploy
      - key: STX_PASSWORD
        value: stx
    healthCheckPath: /_stcore/health
```

### 5.4 Suppression du sys.path hack

Chaque `setup.py` dans les manuels peut être **simplifié ou supprimé** :

```python
# AVANT (setup.py avec sys.path hack)
try:
    import streamtex
except ImportError:
    import os, sys
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# APRÈS (plus besoin de setup.py pour l'import)
# streamtex est installé via pip/uv, l'import fonctionne nativement
import streamtex as sx
```

### 5.5 Migration Git avec historique

Pour conserver l'historique Git des fichiers migrés :

```bash
# 1. Cloner le monorepo
git clone https://github.com/nicolasguelfi/streamtex.git streamtex-manuals
cd streamtex-manuals

# 2. Filtrer pour ne garder que les dossiers manuals
# Utiliser git-filter-repo (pip install git-filter-repo)
git filter-repo \
  --path documentation/manuals/stx_manual_intro/ \
  --path documentation/manuals/stx_manual_advanced/ \
  --path documentation/manuals/stx_manual_deploy/ \
  --path documentation/manuals/stx_manuals_collection/ \
  --path documentation/manuals/stx_manuals_shared-blocks/

# 3. Restructurer (déplacer les dossiers à la racine)
git filter-repo --path-rename documentation/manuals/:

# 4. Créer le nouveau repo sur GitHub
gh repo create nicolasguelfi/streamtex-manuals --public

# 5. Pousser
git remote add origin https://github.com/nicolasguelfi/streamtex-manuals.git
git push -u origin main
```

**Note** : `git-filter-repo` est l'outil recommandé (remplaçant de `git filter-branch`). Installer avec `pip install git-filter-repo`.

---

## 6. Phase 3 — Indépendance des projets utilisateur

### 6.1 Objectif

Rendre le projet AI4SE autonome dans son propre repo avec son propre déploiement Render.

### 6.2 Structure du repo ai4se-streamtex

```
nicolasguelfi/ai4se-streamtex
├── book.py
├── blocks/
│   ├── __init__.py
│   ├── helpers.py
│   ├── bck_*.py
│   └── ...
├── custom/
│   ├── styles.py
│   └── ...
├── static/
│   └── images/
├── .streamlit/
│   └── config.toml
├── Dockerfile
├── render.yaml
├── pyproject.toml
├── uv.lock
├── CLAUDE.md                    # Instructions spécifiques au projet
└── README.md
```

### 6.3 pyproject.toml du projet

```toml
[project]
name = "ai4se-streamtex"
version = "1.0.0"
requires-python = ">=3.10"
dependencies = [
    "streamtex>=0.3.0",
    "streamlit>=1.54.0",
]
```

### 6.4 Dockerfile du projet

```dockerfile
FROM python:3.13-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app
ENV UV_LINK_MODE=copy

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY . .

EXPOSE 8501
HEALTHCHECK CMD curl -f http://localhost:8501/_stcore/health
CMD ["uv", "run", "streamlit", "run", "book.py", \
     "--server.port=8501", "--server.address=0.0.0.0", \
     "--server.headless=true"]
```

### 6.5 render.yaml du projet

```yaml
services:
  - type: web
    name: ai4se-streamtex
    runtime: docker
    repo: https://github.com/nicolasguelfi/ai4se-streamtex
    branch: main
    plan: free
    dockerfilePath: ./Dockerfile
    dockerContext: .
    envVars:
      - key: STX_PASSWORD
        value: stx
    healthCheckPath: /_stcore/health
```

### 6.6 Quota Render (free tier)

**Attention** : Chaque service Render (même dans des repos différents) partage le quota de 750 heures/mois du **même compte Render**.

| Après séparation | Services | Heures estimées/mois |
|------------------|----------|---------------------|
| Manuals | 4 services | ~200h (sleep après 15 min) |
| AI4SE | 1 service | ~50h |
| **Total** | **5 services** | **~250h** (dans le quota) |

Si plus de services sont ajoutés, envisager :
- Le **plan Starter** Render ($7/mois par service, pas de sleep)
- Regrouper certains services sur un seul conteneur

---

## 7. Phase 4 — Renommage des services Render

### 7.1 Correspondance ancien → nouveau

| Ancien nom | Ancienne URL | Nouveau nom | Nouvelle URL |
|-----------|-------------|------------|-------------|
| `streamtex` | `streamtex.onrender.com` | `streamtex` | `streamtex.onrender.com` (inchangé) |
| `streamtex-intro` | `streamtex-intro.onrender.com` | `intro-manual-streamtex` | `intro-manual-streamtex.onrender.com` |
| `streamtex-advanced` | `streamtex-advanced.onrender.com` | `advanced-manual-streamtex` | `advanced-manual-streamtex.onrender.com` |
| `streamtex-deploy` | `streamtex-deploy.onrender.com` | `deploy-manual-streamtex` | `deploy-manual-streamtex.onrender.com` |
| *(nouveau)* | — | `ai4se-streamtex` | `ai4se-streamtex.onrender.com` |

### 7.2 Procédure de renommage sur Render

**Important** : Render ne permet pas de renommer un service. Il faut supprimer et recréer.

```
Pour chaque service à renommer :

1. Aller sur dashboard.render.com
2. Sélectionner le service (ex: streamtex-intro)
3. Settings → noter toutes les variables d'environnement
4. Supprimer le service (Delete Service)
5. Créer un nouveau service avec le nouveau nom (intro-manual-streamtex)
   - Connecter le même repo GitHub
   - Configurer les mêmes variables d'environnement
   - Configurer le même Dockerfile

Alternative (recommandée) :
   - Utiliser le Blueprint (render.yaml) avec les nouveaux noms
   - Dashboard → Blueprints → Sync → les nouveaux services sont créés
   - Supprimer manuellement les anciens services
```

### 7.3 Mise à jour des références croisées

Après renommage, mettre à jour :

1. **`collection.toml`** dans le hub :
   ```toml
   [projects.test-intro]
   project_url = "https://intro-manual-streamtex.onrender.com"

   [projects.test-advanced]
   project_url = "https://advanced-manual-streamtex.onrender.com"

   [projects.test-deploy]
   project_url = "https://deploy-manual-streamtex.onrender.com"
   ```

2. **Variables d'environnement Render** du hub :
   ```
   STX_URL_TEST_INTRO=https://intro-manual-streamtex.onrender.com
   STX_URL_TEST_ADVANCED=https://advanced-manual-streamtex.onrender.com
   STX_URL_TEST_DEPLOY=https://deploy-manual-streamtex.onrender.com
   ```

3. **README** et documentation avec les nouvelles URLs

---

## 8. Matrice des risques

| Risque | Impact | Probabilité | Mitigation |
|--------|--------|-------------|------------|
| Nom `streamtex` pris sur PyPI entre-temps | Élevé | Faible | Publier rapidement une version placeholder |
| Casser les imports existants | Élevé | Moyen | Tester dans un venv isolé avant de publier |
| Perte d'historique Git | Moyen | Faible | Utiliser `git-filter-repo`, garder une archive du monorepo |
| Downtime pendant la migration Render | Faible | Élevé | Créer les nouveaux services AVANT de supprimer les anciens |
| Dépassement quota Render free tier | Moyen | Faible | Monitorer les heures via le dashboard |
| Incohérence de versions lib/projets | Moyen | Moyen | Pinning dans pyproject.toml (`streamtex>=0.3.0,<1.0`) |
| Shared blocks cassés après séparation | Moyen | Moyen | Tests d'intégration avant la migration |

---

## 9. Calendrier recommandé

| Phase | Durée estimée | Pré-requis |
|-------|--------------|------------|
| **Phase 1** : PyPI | 1-2 sessions | Compte PyPI, nettoyage pyproject.toml |
| **Phase 2** : Manuals repo | 1 session | Phase 1 terminée (lib sur PyPI) |
| **Phase 3** : AI4SE | 1 session | Phase 1 terminée |
| **Phase 4** : Renommage Render | 1 session | Phases 2 et 3 terminées |

**Ordre recommandé** : Phase 1 → (Phase 2 + Phase 3 en parallèle) → Phase 4

> Les phases 2 et 3 peuvent être faites en parallèle car elles sont indépendantes. La phase 4 (renommage URLs) doit être faite en dernier car elle touche les services en production.

---

## Annexe A — Migration vers un domaine personnalisé

### A.1 Pourquoi un domaine personnalisé ?

La convention Render (`{nom}.onrender.com`) ne permet pas la notation pointée.
Avec un domaine personnalisé, tu obtiens :

| Type | URL |
|------|-----|
| Hub | `streamtex.io` |
| Manuel intro | `intro.manual.streamtex.io` |
| Manuel avancé | `advanced.manual.streamtex.io` |
| Manuel deploy | `deploy.manual.streamtex.io` |
| Projet AI4SE | `ai4se.streamtex.io` |

### A.2 Choix du domaine

| Domaine | Disponibilité | Prix/an | Commentaire |
|---------|--------------|---------|-------------|
| `streamtex.io` | À vérifier | ~30-50€ | Extension tech populaire |
| `streamtex.dev` | À vérifier | ~12-15€ | Extension développeur (Google) |
| `streamtex.app` | À vérifier | ~12-15€ | Extension application (Google) |
| `streamtex.org` | À vérifier | ~10-12€ | Extension classique |

**Recommandation** : `streamtex.dev` — professionnel, abordable, HTTPS forcé par défaut.

### A.3 Procédure de configuration

#### Étape 1 : Acheter le domaine

Registraires recommandés :
- **Cloudflare Registrar** — Prix coûtant, DNS intégré, gratuit pour le DNS
- **Namecheap** — Interface simple, prix compétitifs
- **Google Domains** (via Squarespace) — Intégration simple

#### Étape 2 : Configurer le DNS

Ajouter des enregistrements CNAME pour chaque sous-domaine :

```
# Fichier zone DNS
@                    CNAME   streamtex.onrender.com.
intro.manual         CNAME   intro-manual-streamtex.onrender.com.
advanced.manual      CNAME   advanced-manual-streamtex.onrender.com.
deploy.manual        CNAME   deploy-manual-streamtex.onrender.com.
ai4se                CNAME   ai4se-streamtex.onrender.com.
```

> **Note** : L'enregistrement `@` (apex/racine) ne peut pas être un CNAME standard.
> Solutions :
> - Utiliser Cloudflare avec CNAME Flattening (gratuit)
> - Ou pointer `www.streamtex.dev` et rediriger `streamtex.dev` → `www.streamtex.dev`

#### Étape 3 : Configurer les Custom Domains sur Render

Pour chaque service :

1. Dashboard Render → Sélectionner le service
2. Settings → Custom Domains → Add Custom Domain
3. Entrer le sous-domaine (ex: `intro.manual.streamtex.dev`)
4. Render génère automatiquement un certificat TLS (Let's Encrypt)
5. Attendre la propagation DNS (quelques minutes à 48h)

#### Étape 4 : Vérification

```bash
# Vérifier la résolution DNS
dig intro.manual.streamtex.dev CNAME

# Vérifier le certificat TLS
curl -vI https://intro.manual.streamtex.dev 2>&1 | grep "SSL certificate"

# Vérifier que le service répond
curl -s https://intro.manual.streamtex.dev/_stcore/health
```

### A.4 Coût total

| Poste | Coût/an |
|-------|---------|
| Domaine `.dev` | ~15€ |
| DNS (Cloudflare) | Gratuit |
| Custom domains Render | Gratuit (inclus dans le plan) |
| Certificats TLS | Gratuit (Let's Encrypt via Render) |
| **Total** | **~15€/an** |

---

## Annexe B — Migration vers une organisation GitHub

### B.1 Quand migrer ?

Migrer vers une organisation GitHub quand :
- D'autres contributeurs rejoignent le projet
- Tu veux séparer tes projets personnels de la librairie open-source
- Tu veux des fonctionnalités d'équipe (code review, teams, permissions)

### B.2 Créer l'organisation

1. GitHub → Settings → Organizations → New Organization
2. Nom recommandé : `streamtex-org` (ou `streamtex` si disponible)
3. Plan : Free (suffisant pour l'open-source)

### B.3 Transférer les repos

Pour chaque repo à transférer :

1. Aller dans le repo → Settings → Danger Zone → Transfer Repository
2. Sélectionner l'organisation cible
3. GitHub crée automatiquement une **redirection** depuis l'ancien chemin

```
nicolasguelfi/streamtex      → streamtex-org/streamtex
nicolasguelfi/streamtex-manuals → streamtex-org/streamtex-manuals
```

> **Important** : Les redirections GitHub fonctionnent pour `git clone` et les URLs web. Les services Render continueront à fonctionner grâce à ces redirections. Il est tout de même recommandé de mettre à jour les URLs dans les `render.yaml`.

### B.4 Impact sur PyPI

Le Trusted Publishing PyPI doit être mis à jour :
1. PyPI → Account Settings → Publishing
2. Modifier le publisher : `nicolasguelfi/streamtex` → `streamtex-org/streamtex`

### B.5 Impact sur Render

Mettre à jour le champ `repo` dans chaque `render.yaml` :
```yaml
repo: https://github.com/streamtex-org/streamtex-manuals
```

Puis re-synchroniser le Blueprint sur le dashboard Render.

---

## Annexe C — Architecture shared-blocks en multi-repo

### C.1 Problématique

En monorepo, les blocs partagés sont simplement un dossier référencé par chemin relatif.
En multi-repo, il faut un mécanisme pour que les projets accèdent aux blocs partagés.

### C.2 Patterns possibles

#### Pattern 1 : Shared blocks dans le repo manuals (recommandé pour les manuels)

```
streamtex-manuals/
├── stx_manual_intro/
├── stx_manual_advanced/
├── shared-blocks/          ← Blocs partagés entre manuels
│   ├── blocks/
│   │   ├── bck_header_training.py
│   │   ├── bck_footer_training.py
│   │   └── ...
│   ├── custom/
│   └── static/
└── Dockerfile              ← Copie shared-blocks/ dans chaque conteneur
```

**Avantage** : Simplicité — un seul repo à maintenir pour tous les manuels.

#### Pattern 2 : Repo dédié shared-blocks (recommandé pour les utilisateurs)

```
nicolasguelfi/my-shared-blocks
├── blocks/
│   ├── bck_common_header.py
│   ├── bck_common_footer.py
│   └── ...
├── custom/
│   └── shared_styles.py
├── static/
│   └── logos/
└── pyproject.toml          ← Package installable (optionnel)
```

Chaque projet le référence comme **git submodule** ou **dépendance pip** :

**Option A : Git submodule**
```bash
# Dans le repo du projet
git submodule add https://github.com/nicolasguelfi/my-shared-blocks.git shared-blocks
```

```python
# Dans book.py
from streamtex import set_static_sources
set_static_sources(["static", "shared-blocks/static"])
```

**Option B : Package pip** (si publié sur PyPI)
```toml
# pyproject.toml du projet
dependencies = [
    "streamtex>=0.3.0",
    "my-shared-blocks>=1.0.0",
]
```

#### Pattern 3 : Blocs partagés intégrés à la librairie streamtex

Réservé aux blocs **universels** que tout utilisateur StreamTeX pourrait vouloir (ex: templates de header/footer standards). Pas recommandé pour les blocs spécifiques à un groupe de projets.

### C.3 Recommandation par contexte

| Contexte | Pattern recommandé |
|----------|-------------------|
| Manuels StreamTeX | Pattern 1 (dans le repo manuals) |
| Projets utilisateur partageant des blocs | Pattern 2 (repo dédié + submodule) |
| Blocs universels pour tous les utilisateurs | Pattern 3 (dans la librairie) |

### C.4 LazyBlockRegistry en multi-repo

Le `LazyBlockRegistry` existant supporte déjà le multi-source :

```python
from streamtex import LazyBlockRegistry

registry = LazyBlockRegistry()
registry.add_source("blocks")              # Blocs locaux du projet
registry.add_source("shared-blocks/blocks") # Blocs partagés (submodule ou copie)

# Priorité : le bloc local gagne si même nom dans les deux sources
block = registry.get("bck_header_training")
```

---

## Annexe D — Checklist de validation par phase

### Phase 1 : Publication PyPI

- [ ] Compte PyPI créé
- [ ] Nom `streamtex` réservé (publier une v0.3.0-alpha si besoin)
- [ ] `pyproject.toml` enrichi (metadata, URLs, classifiers)
- [ ] README.md orienté utilisateur créé
- [ ] `uv build` produit les artifacts correctement
- [ ] Publication test sur TestPyPI réussie
- [ ] `pip install streamtex` fonctionne dans un venv vierge
- [ ] `import streamtex as sx; sx.st_write(...)` fonctionne
- [ ] Workflow GitHub Actions `publish.yml` configuré
- [ ] Trusted Publishing OIDC configuré sur PyPI
- [ ] Première release GitHub créée → publication automatique PyPI
- [ ] Tests CI passent sur le repo nettoyé

### Phase 2 : Séparation Manuals

- [ ] Repo `streamtex-manuals` créé sur GitHub
- [ ] Historique Git préservé (via `git-filter-repo`)
- [ ] `pyproject.toml` avec `streamtex>=0.3.0` comme dépendance
- [ ] `uv sync` installe streamtex depuis PyPI
- [ ] Tous les `setup.py` nettoyés (plus de `sys.path` hack)
- [ ] `Dockerfile` ne copie plus `streamtex/` source
- [ ] Build Docker local fonctionne
- [ ] Les 4 manuels se lancent correctement
- [ ] Shared-blocks fonctionnent dans les manuels advanced/collection
- [ ] `render.yaml` avec les nouveaux noms de services
- [ ] CI (tests + Docker build) configuré

### Phase 3 : Indépendance AI4SE

- [ ] Repo `ai4se-streamtex` créé sur GitHub
- [ ] Projet AI4SE copié et restructuré
- [ ] `pyproject.toml` avec `streamtex>=0.3.0`
- [ ] `setup.py` supprimé ou nettoyé
- [ ] Build Docker local fonctionne
- [ ] `render.yaml` avec le service `ai4se-streamtex`
- [ ] Le projet se lance correctement
- [ ] CLAUDE.md adapté au contexte standalone

### Phase 4 : Renommage Render

- [ ] Nouveaux services créés via Blueprint (render.yaml)
- [ ] Vérification que chaque service répond sur sa nouvelle URL
- [ ] Variables d'environnement du hub mises à jour (STX_URL_*)
- [ ] `collection.toml` mis à jour avec les nouvelles URLs
- [ ] Anciens services supprimés
- [ ] Toute la documentation mise à jour avec les nouvelles URLs
- [ ] Aucun lien cassé dans les manuels

### Post-migration

- [ ] Monorepo original archivé (ou converti en "pointer repo" avec README)
- [ ] Tous les repos ont un CI fonctionnel
- [ ] Versions de streamtex pinnées dans chaque projet
- [ ] Documentation mise à jour dans le README de chaque repo
