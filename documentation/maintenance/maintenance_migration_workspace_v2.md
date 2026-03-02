# Plan de Maintenance : Migration Workspace Multi-Repo & CLI `stx`

> **Date** : 2026-03-01
> **Auteur** : Nicolas Guelfi + Claude
> **Version** : 2.0
> **Statut** : DONE (Phases 1-6 DONE)
> **Predecesseur** : `maintenance_separation_multirepo.md` (v1.0, 2026-02-25)

est-ce que à côté du dossier streamtex dans lequel nous sommes actuellement serait le bon choix ?
ça serait donc ici:
/Volumes/Mac_Data/Win_data/data/backups/Dropbox-nicolas.guelfi@laposte.net/messir Dropbox/Nicolas Guelfi/users/NG/dev-dropbox/dvlpt/eclipse/git/github/streamtex-dev
---

## Table des matieres

1. [Resume executif](#1-resume-executif)
2. [Diagnostic de l'etat actuel](#2-diagnostic-de-letat-actuel)
3. [Architecture cible](#3-architecture-cible)
4. [CLI `stx` — Specification complete](#4-cli-stx--specification-complete)
5. [Phase 1 : Publication PyPI — DONE](#5-phase-1--publication-pypi--done-2026-03-01-commit-c7d6d8d)
6. [Phase 2 : Repo `streamtex-claude` — DONE](#6-phase-2--repo-streamtex-claude--done-2026-03-01)
7. [Phase 3 : Separation repo `streamtex-docs` — DONE](#7-phase-3--separation-repo-streamtex-docs--done-2026-03-02-commit-1cf89a6)
8. [Phase 4 : Autonomisation des projets](#8-phase-4--autonomisation-des-projets)
9. [Phase 5 : Nettoyage du repo librairie — DONE](#9-phase-5--nettoyage-du-repo-librairie--done-2026-03-02-commit-7fd7d4f)
10. [Phase 6 : Script CLI `stx` et workspace](#10-phase-6--script-cli-stx-et-workspace)
11. [Matrice des risques](#11-matrice-des-risques)
12. [Calendrier recommande](#12-calendrier-recommande)
13. [Annexe A : Mapping fichiers actuel → cible](#annexe-a--mapping-fichiers-actuel--cible)
14. [Annexe B : Profils Claude AI — Contenu detaille](#annexe-b--profils-claude-ai--contenu-detaille)
15. [Annexe C : Templates de fichiers cles](#annexe-c--templates-de-fichiers-cles)
16. [Annexe D : Checklist de validation par phase](#annexe-d--checklist-de-validation-par-phase)

---

## 1. Resume executif

### 1.1 Objectif

Migrer le monorepo `streamtex` vers un ecosysteme multi-repo professionnel permettant :

1. **Publication PyPI** de la librairie `streamtex`
2. **Distribution autonome** de la configuration Claude AI (3 profils)
3. **Deploiement independant** des manuels et des projets utilisateur
4. **Workflow de developpement local** unifie via un CLI `stx`
5. **Deploiement multi-plateforme** (Render, HuggingFace, Docker) via `stx deploy`

### 1.2 Decisions cles

| Aspect | Decision |
|--------|----------|
| **PyPI** | Package `streamtex`, public, semantic versioning |
| **Compte GitHub** | `nicolasguelfi` (migration org possible plus tard) |
| **Repos** | 4 repos principaux + N repos projets |
| **Dev local** | `uv` workspaces avec `[tool.uv.sources]` pour editable installs |
| **Claude AI** | Repo dedie `streamtex-claude` avec 4 profils installables |
| **CLI** | Script Python `stx` installable via `pipx` ou `uv tool` |
| **Deploy** | Abstraction generique dans `stx deploy` (Render, HuggingFace, Docker) |
| **Premiere version** | `0.3.0` (premier release PyPI public) |

### 1.3 Personas

| Persona | Role | Repos utilises |
|---------|------|---------------|
| **Nicolas (lib)** | Developpe la librairie streamtex | `streamtex` |
| **Nicolas (docs)** | Developpe les manuels utilisateur | `streamtex-docs` + `streamtex` (editable) |
| **Nicolas (projet)** | Developpe des projets de formation | `ai4se-streamtex` + `streamtex` (editable) |
| **Nicolas (claude)** | Maintient la config Claude AI | `streamtex-claude` |
| **Bob (utilisateur)** | Cree et deploie des projets StreamTeX | Son projet + `streamtex` (PyPI) + `streamtex-claude` (install) |

---

## 2. Diagnostic de l'etat actuel

### 2.1 Structure monorepo actuelle

```
streamtex/                          ← UN SEUL REPO GIT
├── streamtex/                      # Librairie Python (37 modules + styles/)
│   ├── __init__.py                 # 97 lignes, re-exports publics
│   ├── write.py, grid.py, ...      # Modules de rendu
│   ├── styles/                     # Sous-package (6 fichiers)
│   └── static/default.css          # CSS distribue avec le package
├── tests/                          # 19 fichiers, 203 tests
├── documentation/
│   ├── coding_standards.md         # Source unique de verite
│   ├── streamtex_cheatsheet_en.md  # Reference syntaxe
│   ├── streamtex_cheatsheet_fr.md
│   ├── template_project/           # Template projet standard
│   ├── template_collection/        # Template collection
│   ├── maintenance/                # 14 plans de maintenance
│   └── manuals/
│       ├── stx_manual_intro/       # 14 blocs atomiques + 16 composites
│       ├── stx_manual_advanced/    # 35 blocs atomiques + 22 composites
│       ├── stx_manual_deploy/      # 3 atomiques + 9 composites
│       ├── stx_manuals_collection/ # Hub collection (1 bloc)
│       └── stx_manuals_shared-blocks/  # 5 blocs partages
├── projects/
│   ├── AI4SE/                      # Projet actif (3 blocs, CLAUDE.md propre)
│   ├── project_aiai18h/            # Projet actif (24 blocs)
│   ├── project_html_example/       # Projet migration (2 blocs)
│   ├── project_modelsward/         # Projet actif (22 blocs)
│   ├── convert_html_to_streamtex/  # Pipeline conversion (~360 blocs)
│   ├── AIDAY/                      # Notes seulement (pas un projet STX)
│   └── modelsward/                 # Materiaux (pas un projet STX)
├── .claude/
│   ├── settings.json               # Permissions Claude Code
│   ├── memory/MEMORY.md            # Memoire projet
│   ├── commands/                   # 23 slash commands (4 categories)
│   │   ├── designer/ (10)
│   │   ├── developer/ (3)
│   │   ├── migration/ (5)
│   │   └── project/ (4)
│   ├── designer/                   # Skills + agents design
│   │   ├── skills/ (3)
│   │   ├── agents/ (2)
│   │   └── ros_designer_default/   # Role presentation (2 skills, 1 agent)
│   └── developer/
│       └── skills/ (2)             # architecture, testing-patterns
├── deploy/                         # Scripts deploiement (11 fichiers)
├── .github/workflows/ci.yml       # CI/CD
├── Dockerfile                      # Multi-projet avec ARG FOLDER
├── docker-compose.yml              # 3 services manuels
├── render.yaml                     # 4 services Render
├── pyproject.toml                  # name=streamtex, version=0.2.0
├── CLAUDE.md                       # Regles projet globales (205 lignes)
└── run-test-projects.sh            # Lance manuels en parallele
```

### 2.2 Problemes identifies

| # | Probleme | Impact | Severite |
|---|----------|--------|----------|
| P1 | Librairie non publiable sur PyPI en l'etat | Bob ne peut pas `pip install streamtex` | Critique |
| P2 | Claude AI config non distribuable | Bob n'a pas d'aide Claude pour ses projets | Critique |
| P3 | Tous les projets dans le meme repo | Pas de deploiement independant | Majeur |
| P4 | Hack `sys.path` dans `setup.py` des projets | Fragile, casse si structure change | Majeur |
| P5 | Manuels couples a la librairie | Impossible de deployer les docs seules | Majeur |
| P6 | Dockerfile copie toute la librairie | Images Docker inutilement grosses post-PyPI | Mineur |
| P7 | `render.yaml` reference un seul repo | Tous les services pointent vers le monorepo | Majeur |
| P8 | Pas de workflow "nouveau projet" automatise | Bob doit copier manuellement | Mineur |
| P9 | `MEMORY.md` depasse 200 lignes (tronque) | Perte de contexte Claude entre sessions | Mineur |

### 2.3 Ce qui fonctionne bien (a conserver)

- Architecture librairie solide (37 modules, dual rendering, DI pattern)
- 203 tests passants, CI/CD fonctionnel
- Hybrid block helpers system (3 modes d'usage)
- LazyBlockRegistry multi-source
- Scripts de deploiement (Render, HuggingFace, Docker, Ansible)
- 23 slash commands Claude bien structures
- Templates projet et collection fonctionnels

---

## 3. Architecture cible

### 3.1 Vue d'ensemble des repos

```
nicolasguelfi (GitHub)
├── streamtex                    REPO 1 : Librairie Python → PyPI
├── streamtex-docs               REPO 2 : Manuels + documentation
├── streamtex-claude             REPO 3 : Config Claude AI (4 profils)
├── ai4se-streamtex              REPO 4 : Projet AI4SE
├── aiai18h-streamtex            REPO 5 : Projet AIAI18H
└── modelsward-streamtex         REPO 6 : Projet MODELSWARD
```

### 3.2 Flux de dependances

```
                    ┌─────────────────┐
                    │   PyPI          │
                    │   streamtex     │
                    │   >= 0.3.0      │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
              ▼              ▼              ▼
     ┌────────────┐  ┌─────────────┐  ┌──────────┐
     │ streamtex  │  │ streamtex   │  │ projet   │
     │ -docs      │  │ -claude     │  │ user     │
     │            │  │ (reference  │  │          │
     │ pip install│  │  only, no   │  │ pip inst.│
     │ streamtex  │  │  runtime    │  │ streamtex│
     └────────────┘  │  dep)       │  └─────┬────┘
                     └──────┬──────┘        │
                            │               │
                            └───────────────┘
                         stx claude install
                         (copie les fichiers
                          .claude/ dans le projet)
```

### 3.3 Workspace de developpement local (Nicolas)

```
~/dev/streamtex-dev/                    ← Dossier workspace parent
│
├── streamtex/                          ← REPO 1 clone
│   ├── streamtex/                      # Package Python
│   ├── tests/
│   ├── .claude/                        # Profil "library" (installe depuis streamtex-claude)
│   ├── CLAUDE.md
│   ├── pyproject.toml
│   └── .github/workflows/
│       ├── ci.yml                      # Tests + lint
│       └── publish.yml                 # PyPI Trusted Publishing
│
├── streamtex-docs/                     ← REPO 2 clone
│   ├── manuals/
│   │   ├── stx_manual_intro/
│   │   ├── stx_manual_advanced/
│   │   ├── stx_manual_deploy/
│   │   ├── stx_manuals_collection/
│   │   └── shared-blocks/
│   ├── references/
│   │   ├── coding_standards.md
│   │   └── streamtex_cheatsheet_en.md
│   ├── templates/
│   │   ├── template_project/
│   │   └── template_collection/
│   ├── .claude/                        # Profil "documentation"
│   ├── CLAUDE.md
│   ├── pyproject.toml                  # depends: streamtex>=0.3.0
│   ├── render.yaml
│   └── Dockerfile
│
├── streamtex-claude/                   ← REPO 3 clone
│   ├── profiles/
│   │   ├── project/                    # Profil Bob (dev projet)
│   │   ├── presentation/              # Profil presentations live
│   │   ├── library/                    # Profil Nicolas (dev lib)
│   │   └── documentation/             # Profil Nicolas (dev docs)
│   ├── shared/                         # Ressources partagees entre profils
│   │   ├── references/
│   │   └── snippets/
│   ├── install.py
│   └── README.md
│
├── projects/                           ← Dossier local projets
│   ├── ai4se-streamtex/               ← REPO 4 clone
│   ├── aiai18h-streamtex/             ← REPO 5 clone
│   └── modelsward-streamtex/          ← REPO 6 clone
│
└── stx.toml                           ← Configuration workspace (genere par stx init)
```

### 3.4 Gestion des dependances : Dev vs Production

#### En developpement (Nicolas) — editable installs via `[tool.uv.sources]`

Chaque repo projet/docs contient dans son `pyproject.toml` :

```toml
# pyproject.toml du repo streamtex-docs (ou d'un projet)
[project]
dependencies = ["streamtex>=0.3.0"]

# Override pour dev local — ignore par pip install, utilise par uv sync
[tool.uv.sources]
streamtex = { path = "../streamtex", editable = true }
```

**Comportement** :
- `uv sync` dans `streamtex-docs/` → installe `streamtex` en editable depuis `../streamtex/`
- `pip install streamtex-docs` → installe `streamtex>=0.3.0` depuis PyPI
- Le switch dev/prod est **automatique** selon l'outil utilise

#### En production (Bob)

```toml
# pyproject.toml du projet de Bob
[project]
dependencies = ["streamtex>=0.3.0"]
# Pas de [tool.uv.sources] → toujours PyPI
```

### 3.5 Convention de nommage

| Element | Convention | Exemple |
|---------|-----------|---------|
| Repo librairie | `streamtex` | `nicolasguelfi/streamtex` |
| Repo docs | `streamtex-docs` | `nicolasguelfi/streamtex-docs` |
| Repo Claude | `streamtex-claude` | `nicolasguelfi/streamtex-claude` |
| Repo projet | `{nom}-streamtex` | `nicolasguelfi/ai4se-streamtex` |
| Service Render | `streamtex-{suffixe}` | `streamtex-intro.onrender.com` |
| Package PyPI | `streamtex` | `pip install streamtex` |
| Profil Claude | `project`, `presentation`, `library`, `documentation` | `stx claude install project` |

---

## 4. CLI `stx` — Specification complete

### 4.1 Vue d'ensemble

Le CLI `stx` est un outil Python autonome qui unifie la gestion du workspace multi-repo, l'installation des profils Claude, et le deploiement multi-plateforme.

**Installation** :
```bash
# Option 1 : via uv tool (recommande)
uv tool install streamtex-cli
# → Installe la commande `stx` globalement

# Option 2 : via pipx
pipx install streamtex-cli

# Option 3 : depuis le repo (dev)
cd ~/dev/streamtex-dev/streamtex
uv run stx --help
```

**Ou heberger le code `stx`** : Dans le repo `streamtex` lui-meme, sous `streamtex/cli/` ou comme entry point console dans `pyproject.toml`.

### 4.2 Arborescence du CLI

```
stx
├── workspace
│   ├── init <path>              # Initialise un workspace
│   ├── clone                    # Clone tous les repos
│   ├── link                     # Configure les editable installs
│   ├── status                   # Etat de tous les repos
│   └── sync                     # uv sync dans tous les repos
│
├── claude
│   ├── install <profile> [path] # Installe un profil Claude AI
│   ├── update [path]            # Met a jour le profil installe
│   ├── list                     # Liste les profils disponibles
│   └── diff [path]              # Compare l'installe vs le repo
│
├── project
│   ├── new <name> [--profile]   # Cree un nouveau projet
│   ├── upgrade <path>           # Met a jour le boilerplate
│   └── validate <path>          # Verifie la structure
│
├── deploy
│   ├── preflight [path]         # Checks pre-deploiement
│   ├── docker <path> [--port]   # Build + run Docker local
│   ├── render <path> [opts]     # Deploy sur Render.com
│   ├── huggingface <path> <url> # Deploy sur HuggingFace Spaces
│   └── status <platform> [name] # Statut d'un deploiement
│
├── publish
│   ├── pypi [--test]            # Publie sur PyPI (ou TestPyPI)
│   └── check                    # Verifie la readiness PyPI
│
├── test                         # Raccourci: uv run pytest tests/ -v
└── lint                         # Raccourci: uv run ruff check streamtex/
```

### 4.3 `stx workspace` — Gestion du workspace

#### `stx workspace init <path>`

Cree le dossier workspace et le fichier `stx.toml` de configuration.

```bash
stx workspace init ~/dev/streamtex-dev
```

Genere `~/dev/streamtex-dev/stx.toml` :

```toml
# stx.toml — StreamTeX Workspace Configuration
# Genere par: stx workspace init
# Date: 2026-03-01

[workspace]
name = "streamtex-dev"
created = "2026-03-01"

[repos]
# Format: nom = { url = "...", path = "...", type = "library|docs|claude|project" }

[repos.streamtex]
url = "https://github.com/nicolasguelfi/streamtex.git"
path = "streamtex"
type = "library"

[repos.streamtex-docs]
url = "https://github.com/nicolasguelfi/streamtex-docs.git"
path = "streamtex-docs"
type = "docs"

[repos.streamtex-claude]
url = "https://github.com/nicolasguelfi/streamtex-claude.git"
path = "streamtex-claude"
type = "claude"

# Projets utilisateur — ajouter au fur et a mesure
# [repos.ai4se-streamtex]
# url = "https://github.com/nicolasguelfi/ai4se-streamtex.git"
# path = "projects/ai4se-streamtex"
# type = "project"

[deploy]
# Configuration par defaut pour les deploiements
render_owner = "nicolasguelfi"
render_region = "oregon"
hf_owner = "nicolasguelfi"

[claude]
# Repo source des profils Claude
source = "streamtex-claude"
```

#### `stx workspace clone`

Clone tous les repos declares dans `stx.toml` :

```bash
cd ~/dev/streamtex-dev
stx workspace clone
# → git clone https://github.com/nicolasguelfi/streamtex.git streamtex
# → git clone https://github.com/nicolasguelfi/streamtex-docs.git streamtex-docs
# → git clone https://github.com/nicolasguelfi/streamtex-claude.git streamtex-claude
# → mkdir -p projects
```

#### `stx workspace link`

Configure les editable installs dans chaque repo :

```bash
stx workspace link
# Pour chaque repo de type "docs" ou "project" :
#   cd <repo> && uv sync
# uv lira [tool.uv.sources] et installera streamtex en editable
```

#### `stx workspace status`

Affiche l'etat de tous les repos :

```
StreamTeX Workspace Status
══════════════════════════════════════════════════════════
  streamtex        main  ✓ clean   v0.3.0   12 commits ahead
  streamtex-docs   main  ⚠ 3 changes        up to date
  streamtex-claude main  ✓ clean            up to date
  ai4se-streamtex  main  ✓ clean            2 commits ahead
══════════════════════════════════════════════════════════
```

#### `stx workspace sync`

Execute `uv sync` dans chaque repo du workspace :

```bash
stx workspace sync
# → cd streamtex && uv sync
# → cd streamtex-docs && uv sync
# → cd projects/ai4se-streamtex && uv sync
```

### 4.4 `stx claude` — Gestion des profils Claude AI

#### `stx claude install <profile> [path]`

Installe un profil Claude AI dans un projet.

```bash
# Installe le profil "project" dans le dossier courant
stx claude install project

# Installe le profil "presentation" dans un projet specifique
stx claude install presentation ./projects/ai4se-streamtex

# Installe le profil "library" dans le repo streamtex
stx claude install library ./streamtex
```

**Actions effectuees** :

1. Localise le repo `streamtex-claude` (via `stx.toml` ou chemin par defaut)
2. Copie les fichiers du profil dans `.claude/` du projet cible
3. Copie les ressources partagees (`shared/references/`)
4. Genere `CLAUDE.md` depuis le template du profil
5. Genere `.claude/settings.json` depuis le template
6. Affiche un resume des fichiers installes

**Structure generee** (exemple profil `project`) :

```
<projet>/
├── .claude/
│   ├── settings.json
│   ├── commands/
│   │   ├── designer/
│   │   │   ├── block-new.md
│   │   │   ├── block-preview.md
│   │   │   ├── slide-audit.md
│   │   │   ├── slide-fix.md
│   │   │   ├── slide-new.md
│   │   │   ├── style-audit.md
│   │   │   └── style-refactor.md
│   │   ├── migration/
│   │   │   ├── conversion-audit.md
│   │   │   ├── html-convert-batch.md
│   │   │   ├── html-convert-block.md
│   │   │   ├── html-export.md
│   │   │   └── html-migrate.md
│   │   ├── project/
│   │   │   ├── course-generate.md
│   │   │   ├── project-upgrade.md
│   │   │   └── collection-new.md
│   │   └── developer/
│   │       ├── test-run.md
│   │       └── lint.md
│   ├── designer/
│   │   ├── skills/
│   │   │   ├── visual-design-rules.md
│   │   │   ├── style-conventions.md
│   │   │   └── streamtex-quick-reference.md
│   │   └── agents/
│   │       ├── slide-designer.md
│   │       └── slide-reviewer.md
│   └── references/
│       ├── coding_standards.md
│       └── streamtex_cheatsheet_en.md
└── CLAUDE.md
```

#### `stx claude update [path]`

Met a jour un profil deja installe :

```bash
stx claude update ./projects/ai4se-streamtex
```

1. Detecte le profil installe (stocke dans `.claude/.stx-profile`)
2. Compare les fichiers locaux vs le repo source
3. Met a jour les fichiers modifies (preserve les customisations dans `CLAUDE.md`)
4. Affiche un diff des changements

#### `stx claude list`

Liste les profils disponibles :

```
Available Claude AI Profiles
══════════════════════════════════════════════════════════
  project         Standard StreamTeX project development
                  Commands: designer(7), migration(5), project(3), developer(2)
                  Skills: designer(3), agents(2)

  presentation    Live projection presentations (extends project)
                  Commands: + presentation-audit, presentation-fix, survey-convert
                  Skills: + presentation-design-rules
                  Agents: + presentation-designer

  library         StreamTeX library development
                  Commands: developer(3)
                  Skills: architecture, testing-patterns

  documentation   Manual and documentation authoring
                  Commands: designer(7), project(1), developer(2)
                  Skills: designer(3), agents(2)
══════════════════════════════════════════════════════════
```

### 4.5 `stx project` — Gestion des projets

#### `stx project new <name> [--profile <profile>] [--collection]`

Cree un nouveau projet StreamTeX :

```bash
# Projet standard
stx project new mon-cours

# Projet presentation
stx project new ai4se --profile presentation

# Collection multi-projet
stx project new mes-formations --collection
```

**Actions** :

1. Cree le dossier `<name>-streamtex/` (ou `<name>/` si dans le workspace)
2. Scaffolde la structure complete (book.py, blocks/, custom/, static/, .streamlit/)
3. Initialise un repo git
4. Cree `pyproject.toml` avec dependance `streamtex>=0.3.0`
5. Installe le profil Claude AI demande
6. Execute `uv sync`
7. Si `--collection` : genere aussi `collection.toml` et `blocks/bck_home.py`

#### `stx project validate <path>`

Verifie qu'un projet est complet et valide :

```bash
stx project validate ./projects/ai4se-streamtex
```

```
Project Validation: ai4se-streamtex
══════════════════════════════════════════════════════════
  ✓ book.py found
  ✓ blocks/__init__.py found (ProjectBlockRegistry)
  ✓ custom/styles.py found
  ✓ .streamlit/config.toml found (enableStaticServing=true)
  ✓ pyproject.toml found (streamtex>=0.3.0)
  ✓ .claude/ directory found (profile: presentation)
  ✓ CLAUDE.md found
  ⚠ static/images/ is empty (OK if no assets yet)
  ✓ All block imports resolve
══════════════════════════════════════════════════════════
  Result: VALID (1 warning)
```

### 4.6 `stx deploy` — Deploiement multi-plateforme

Architecture du deploiement : un systeme generique a base de "providers" extensibles.

```python
# Architecture interne (pour reference d'implementation)
class DeployProvider(ABC):
    """Interface pour les providers de deploiement."""
    name: str
    @abstractmethod
    def preflight(self, project_path: Path) -> bool: ...
    @abstractmethod
    def deploy(self, project_path: Path, **kwargs) -> DeployResult: ...
    @abstractmethod
    def status(self, service_name: str) -> ServiceStatus: ...

class RenderProvider(DeployProvider): ...
class HuggingFaceProvider(DeployProvider): ...
class DockerProvider(DeployProvider): ...
# Futur : class StreamlitCloudProvider(DeployProvider): ...
```

#### `stx deploy preflight [path]`

Checks pre-deploiement universels (tous providers) :

```bash
stx deploy preflight ./projects/ai4se-streamtex
```

**Checks effectues** :

| # | Check | Criticite |
|---|-------|-----------|
| 1 | Tests passent (`uv run pytest`) | Bloquant |
| 2 | Lint propre (`uv run ruff check`) | Warning |
| 3 | `book.py` existe | Bloquant |
| 4 | `.streamlit/config.toml` valide | Bloquant |
| 5 | `enableStaticServing = true` | Bloquant |
| 6 | `pyproject.toml` avec `streamtex>=X.Y` | Bloquant |
| 7 | Git working tree propre | Warning |
| 8 | Pas de fichiers sensibles (.env, credentials) | Warning |
| 9 | Assets statiques references existent | Warning |
| 10 | Dockerfile present (si Docker requis) | Conditionnel |

#### `stx deploy docker <path> [--port PORT] [--tag TAG]`

Build et run Docker localement :

```bash
# Build + run sur port 8501
stx deploy docker ./projects/ai4se-streamtex

# Build + run sur port custom
stx deploy docker ./projects/ai4se-streamtex --port 8505

# Build seulement (pas de run)
stx deploy docker ./projects/ai4se-streamtex --build-only --tag ai4se:latest
```

**Actions** :

1. Execute `stx deploy preflight`
2. Si pas de Dockerfile dans le projet, copie le Dockerfile template
3. `docker build --build-arg FOLDER=. -t <tag> .`
4. `docker run -p <port>:8501 <tag>`
5. Attend le healthcheck `/_stcore/health`
6. Affiche l'URL locale

**Dockerfile template** (genere si absent) :

```dockerfile
FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_HEADLESS=true UV_LINK_MODE=copy
WORKDIR /app
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev
COPY . .
ENV PORT=8501
EXPOSE 8501
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health
ENTRYPOINT ["uv", "run", "streamlit", "run", "book.py", \
            "--server.port=8501", "--server.address=0.0.0.0"]
```

#### `stx deploy render <path> [options]`

Deploy sur Render.com :

```bash
# Deploy interactif (guide pas a pas)
stx deploy render ./projects/ai4se-streamtex

# Deploy avec service name specifie
stx deploy render ./projects/ai4se-streamtex --name ai4se-streamtex

# Deploy avec options avancees
stx deploy render ./projects/ai4se-streamtex \
    --name ai4se-streamtex \
    --plan free \
    --branch main \
    --env STX_PASSWORD=secret123
```

**Actions** :

1. Execute `stx deploy preflight`
2. Verifie que le repo est pousse sur GitHub
3. Genere/met a jour `render.yaml` dans le projet :

```yaml
# render.yaml — Genere par stx deploy render
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
        value: changeme
    healthCheckPath: /_stcore/health
    buildFilter:
      paths:
        - "**"
```

4. Pousse le `render.yaml` si modifie
5. Affiche les instructions pour connecter sur Render Dashboard
6. Optionnel : utilise l'API Render pour creer le service automatiquement

**Gestion du `render.yaml` multi-services** (pour le repo docs) :

```bash
# Deploy tous les manuels d'un coup
stx deploy render ./streamtex-docs --multi
```

Genere un `render.yaml` avec N services (un par manual) :

```yaml
services:
  - type: web
    name: streamtex-collection
    runtime: docker
    repo: https://github.com/nicolasguelfi/streamtex-docs
    branch: main
    plan: free
    dockerfilePath: ./Dockerfile
    dockerContext: .
    envVars:
      - key: FOLDER
        value: manuals/stx_manuals_collection
    healthCheckPath: /_stcore/health

  - type: web
    name: streamtex-intro
    # ... idem avec FOLDER=manuals/stx_manual_intro

  - type: web
    name: streamtex-advanced
    # ... idem avec FOLDER=manuals/stx_manual_advanced

  - type: web
    name: streamtex-deploy
    # ... idem avec FOLDER=manuals/stx_manual_deploy
```

#### `stx deploy huggingface <path> <hf_space_url>`

Deploy sur HuggingFace Spaces :

```bash
stx deploy huggingface ./projects/ai4se-streamtex \
    https://huggingface.co/spaces/nicolasguelfi/ai4se-streamtex
```

**Actions** :

1. Execute `stx deploy preflight`
2. Verifie git-lfs installe
3. Verifie token HuggingFace (`huggingface-cli whoami`)
4. Configure LFS tracking pour les assets lourds (`.png`, `.jpg`, `.mp4`, etc.)
5. Genere/verifie le YAML front-matter dans `README.md` :

```yaml
---
title: AI4SE StreamTeX
emoji: "📊"
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 8501
pinned: false
---
```

6. Ajoute/met a jour le remote `hf` :
   ```bash
   git remote add hf https://huggingface.co/spaces/nicolasguelfi/ai4se-streamtex
   ```
7. Propose le push : `git push hf main`
8. Affiche l'URL du Space

**Differences avec Render** :

| Aspect | Render | HuggingFace |
|--------|--------|-------------|
| Config IaC | `render.yaml` | YAML front-matter dans README.md |
| Push | Auto-deploy depuis GitHub | `git push hf main` (remote dedie) |
| Multi-service | Oui (un yaml, N services) | Non (un Space = un projet) |
| Custom domain | Oui ($7/mo plan) | Payant (Pro) |
| Sleep | 15 min (free) | Oui (gratuit) |
| LFS | Non requis | Requis pour assets lourds |

#### `stx deploy status <platform> [name]`

Verifie le statut d'un deploiement :

```bash
# Statut de tous les services Render
stx deploy status render

# Statut d'un service specifique
stx deploy status render ai4se-streamtex

# Statut HuggingFace
stx deploy status huggingface ai4se-streamtex
```

**Output** :

```
Render Deployment Status
══════════════════════════════════════════════════════════
  streamtex-collection   ✓ Live   https://streamtex.onrender.com
  streamtex-intro        ✓ Live   https://streamtex-intro.onrender.com
  streamtex-advanced     ● Sleep  https://streamtex-advanced.onrender.com
  ai4se-streamtex        ✓ Live   https://ai4se-streamtex.onrender.com
══════════════════════════════════════════════════════════
```

### 4.7 `stx publish` — Publication PyPI

#### `stx publish check`

Verifie que le package est pret pour PyPI :

```bash
stx publish check
```

```
PyPI Readiness Check
══════════════════════════════════════════════════════════
  ✓ pyproject.toml valid
  ✓ version: 0.3.0
  ✓ README.md exists
  ✓ LICENSE file exists
  ✓ __version__ matches pyproject.toml
  ✓ No dev dependencies in [project.dependencies]
  ✓ All tests pass
  ✓ ruff check clean
  ✓ Package builds successfully (uv build)
  ✓ twine check passes
══════════════════════════════════════════════════════════
  Ready to publish!
```

#### `stx publish pypi [--test]`

Publie sur PyPI :

```bash
# Publie sur TestPyPI d'abord
stx publish pypi --test

# Publie sur PyPI production
stx publish pypi
```

**Actions** :

1. Execute `stx publish check`
2. Build le package : `uv build`
3. Upload :
   - `--test` : `uv publish --index testpypi`
   - Sans flag : `uv publish`
4. Verifie l'installation : `pip install streamtex==<version>` (dans un venv temporaire)
5. Affiche l'URL PyPI

### 4.8 Implementation technique du CLI

Le CLI sera implemente avec `click` (ou `typer`) et vivra dans le repo `streamtex` :

```
streamtex/
├── streamtex/
│   └── cli/
│       ├── __init__.py
│       ├── main.py              # Point d'entree click/typer
│       ├── workspace.py         # Commandes workspace
│       ├── claude.py            # Commandes claude
│       ├── project.py           # Commandes project
│       ├── deploy/
│       │   ├── __init__.py
│       │   ├── base.py          # DeployProvider ABC
│       │   ├── preflight.py     # Checks universels
│       │   ├── docker.py        # DockerProvider
│       │   ├── render.py        # RenderProvider
│       │   └── huggingface.py   # HuggingFaceProvider
│       ├── publish.py           # Commandes publish
│       └── templates/           # Templates de fichiers
│           ├── Dockerfile.j2
│           ├── render.yaml.j2
│           ├── pyproject.toml.j2
│           ├── book.py.j2
│           └── CLAUDE.md.j2
```

**Entry point** dans `pyproject.toml` :

```toml
[project.scripts]
stx = "streamtex.cli.main:app"
```

---

## 5. Phase 1 : Publication PyPI — DONE (2026-03-01, commit c7d6d8d)

### 5.1 Objectif

Publier `streamtex` sur PyPI pour que Bob puisse faire `pip install streamtex`.

### 5.2 Pre-requis

- Compte PyPI : `nicolasguelfi` (creer si absent)
- Nom `streamtex` verifie disponible (2026-02-25)
- GitHub Actions : Trusted Publishing configure

### 5.3 Etapes detaillees

#### 5.3.1 Enrichir `pyproject.toml`

Modifications au `pyproject.toml` actuel :

```toml
[project]
name = "streamtex"
version = "0.3.0"                                          # ← bump de 0.2.0
description = "A Streamlit library for styled content rendering with CSS Grid, TOC, markers, and HTML export"
readme = "README.md"                                        # ← changer vers README.md
requires-python = ">=3.10"
license = {text = "MIT"}
keywords = ["streamlit", "presentation", "slides", "css", "html", "export"]
classifiers = [
    "Development Status :: 4 - Beta",
    "Framework :: Streamlit",
    "Intended Audience :: Developers",
    "Intended Audience :: Education",
    "License :: OSI Approved :: MIT License",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: 3.10",
    "Programming Language :: Python :: 3.11",
    "Programming Language :: Python :: 3.12",
    "Programming Language :: Python :: 3.13",
    "Topic :: Text Processing :: Markup :: HTML",
    "Topic :: Multimedia :: Graphics :: Presentation",
]
authors = [
    {name = "Nicolas Guelfi", email = "nicolas.guelfi@laposte.net"},
]

[project.urls]
Homepage = "https://github.com/nicolasguelfi/streamtex"
Documentation = "https://github.com/nicolasguelfi/streamtex-docs"
Repository = "https://github.com/nicolasguelfi/streamtex"
Issues = "https://github.com/nicolasguelfi/streamtex/issues"
Changelog = "https://github.com/nicolasguelfi/streamtex/blob/main/CHANGELOG.md"

[project.scripts]
stx = "streamtex.cli.main:app"                             # ← CLI entry point

[project.optional-dependencies]
inspector = ["streamlit-ace>=0.1.1"]
cli = ["click>=8.0", "rich>=13.0", "jinja2>=3.0"]          # ← deps du CLI

dependencies = [
    "streamlit>=1.54.0",
    "beautifulsoup4>=4.10.0",
    "requests>=2.28.0",
    "watchdog",
    "graphviz>=0.21",
    "matplotlib>=3.10.8",
    "streamlit-mermaid>=0.3.0",
    "mermaid-py>=0.5.0",
    "python-dotenv>=1.2.1",
]
# NOTE: streamlit-ace retire des deps principales → optional [inspector]
```

#### 5.3.2 Creer README.md oriente utilisateur

Contenu cible du `README.md` (a la racine du repo) :

```markdown
# StreamTeX

A Streamlit library for styled content rendering with CSS Grid layouts,
table of contents, navigation markers, and self-contained HTML export.

## Installation

pip install streamtex

## Quick Start

# book.py
from streamtex import *

st_write(Style("font-size:24pt; font-weight:bold;", "title"), "Hello StreamTeX!")

## Features
- CSS-based styling with composition operators (+, -)
- CSS Grid layouts with responsive columns
- Table of Contents with auto-numbering
- Navigation markers (slide-like PageUp/PageDown)
- Self-contained HTML export
- Mermaid, PlantUML, TikZ diagram rendering
- Bibliography management
- Google Sheets integration
- Block helpers with dependency injection

## Documentation
See the interactive manuals: https://streamtex.onrender.com

## License
MIT
```

#### 5.3.3 Creer CHANGELOG.md

```markdown
# Changelog

## [0.3.0] - 2026-03-XX
### Added
- First public PyPI release
- CLI tool `stx` for workspace management and deployment
### Changed
- streamlit-ace moved to optional dependency [inspector]
```

#### 5.3.4 Creer LICENSE

Fichier `LICENSE` MIT a la racine.

#### 5.3.5 Verifier la coherence `__version__`

Dans `streamtex/__init__.py` :
```python
__version__ = "0.3.0"  # ← doit matcher pyproject.toml
```

#### 5.3.6 CI/CD : Workflow `publish.yml`

Nouveau fichier `.github/workflows/publish.yml` :

```yaml
name: Publish to PyPI

on:
  release:
    types: [published]

permissions:
  id-token: write  # Trusted Publishing (OIDC)

jobs:
  publish:
    name: Build and Publish
    runs-on: ubuntu-latest
    environment:
      name: pypi
      url: https://pypi.org/project/streamtex/

    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v4

      - name: Install Python
        run: uv python install

      - name: Install dependencies
        run: uv sync --frozen

      - name: Run tests
        run: uv run pytest tests/ -v

      - name: Lint
        run: uv run ruff check streamtex/

      - name: Build package
        run: uv build

      - name: Publish to PyPI
        uses: pypa/gh-action-pypi-publish@release/v1
        # Trusted Publishing — no token needed, uses OIDC
```

**Configuration Trusted Publishing sur PyPI** :

1. Aller sur https://pypi.org/manage/account/publishing/
2. "Add a new pending publisher" :
   - PyPI project name : `streamtex`
   - Owner : `nicolasguelfi`
   - Repository : `streamtex`
   - Workflow name : `publish.yml`
   - Environment name : `pypi`

#### 5.3.7 Procedure de premiere publication

```bash
# 1. Verifier sur TestPyPI
cd ~/dev/streamtex-dev/streamtex
uv build
uv publish --index testpypi

# 2. Tester l'installation depuis TestPyPI
python -m venv /tmp/test-stx
source /tmp/test-stx/bin/activate
pip install -i https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple/ streamtex==0.3.0
python -c "from streamtex import st_write; print('OK')"
deactivate

# 3. Creer la release GitHub
git tag v0.3.0
git push origin v0.3.0
# → Creer release sur GitHub → declenche publish.yml → publie sur PyPI

# 4. Verifier sur PyPI production
pip install streamtex==0.3.0
```

#### 5.3.8 Politique de versioning

| Type | Bump | Exemple | Quand |
|------|------|---------|-------|
| Patch | `0.3.X` → `0.3.X+1` | `0.3.0` → `0.3.1` | Bug fix, pas de changement d'API |
| Minor | `0.X.0` → `0.X+1.0` | `0.3.0` → `0.4.0` | Nouvelle feature, backward compatible |
| Major | `X.0.0` → `X+1.0.0` | `0.9.0` → `1.0.0` | Breaking change d'API |

**Premiere version stable** : `1.0.0` quand :
- API publique stabilisee
- `__all__` defini dans `__init__.py`
- Type hints complets sur l'API publique
- Documentation complete

---

## 6. Phase 2 : Repo `streamtex-claude` — DONE (2026-03-01)

### 6.1 Objectif

Creer un repo GitHub independant contenant les 4 profils Claude AI, installables dans n'importe quel projet StreamTeX.

### 6.2 Structure du repo

```
streamtex-claude/
├── README.md
├── install.py                          # Script d'installation standalone
├── update.py                           # Script de mise a jour
├── profiles/
│   ├── project/                        # PROFIL 1 : Bob (dev projet standard)
│   │   ├── manifest.toml               # Liste des fichiers du profil
│   │   ├── CLAUDE.md.j2                # Template Jinja2
│   │   ├── settings.json
│   │   ├── commands/
│   │   │   ├── designer/
│   │   │   │   ├── block-new.md
│   │   │   │   ├── block-preview.md
│   │   │   │   ├── slide-audit.md
│   │   │   │   ├── slide-fix.md
│   │   │   │   ├── slide-new.md
│   │   │   │   ├── style-audit.md
│   │   │   │   └── style-refactor.md
│   │   │   ├── migration/
│   │   │   │   ├── conversion-audit.md
│   │   │   │   ├── html-convert-batch.md
│   │   │   │   ├── html-convert-block.md
│   │   │   │   ├── html-export.md
│   │   │   │   └── html-migrate.md
│   │   │   ├── project/
│   │   │   │   ├── course-generate.md
│   │   │   │   ├── project-upgrade.md
│   │   │   │   └── collection-new.md
│   │   │   └── developer/
│   │   │       ├── test-run.md
│   │   │       └── lint.md
│   │   ├── designer/
│   │   │   ├── skills/
│   │   │   │   ├── visual-design-rules.md
│   │   │   │   ├── style-conventions.md
│   │   │   │   └── streamtex-quick-reference.md
│   │   │   └── agents/
│   │   │       ├── slide-designer.md
│   │   │       └── slide-reviewer.md
│   │   └── developer/
│   │       └── skills/
│   │           └── testing-patterns.md  # Utile pour les projets aussi
│   │
│   ├── presentation/                   # PROFIL 2 : Presentations live (etend project)
│   │   ├── manifest.toml
│   │   ├── CLAUDE.md.j2
│   │   ├── extends: project            # Herite de tout le profil project
│   │   └── overlay/                    # Fichiers supplementaires
│   │       ├── commands/designer/
│   │       │   ├── presentation-audit.md
│   │       │   ├── presentation-fix.md
│   │       │   └── survey-convert.md
│   │       └── designer/
│   │           └── ros_designer_default/
│   │               ├── skills/
│   │               │   ├── presentation-design-rules.md
│   │               │   └── survey-chart-conversion.md
│   │               └── agents/
│   │                   └── presentation-designer.md
│   │
│   ├── library/                        # PROFIL 3 : Dev librairie (Nicolas)
│   │   ├── manifest.toml
│   │   ├── CLAUDE.md.j2
│   │   ├── settings.json
│   │   ├── commands/developer/
│   │   │   ├── test-run.md
│   │   │   ├── lint.md
│   │   │   └── deploy.md
│   │   └── developer/skills/
│   │       ├── architecture.md
│   │       └── testing-patterns.md
│   │
│   └── documentation/                  # PROFIL 4 : Dev documentation (Nicolas)
│       ├── manifest.toml
│       ├── CLAUDE.md.j2
│       ├── settings.json
│       ├── commands/
│       │   ├── designer/               # Memes que profil project (7 fichiers)
│       │   ├── project/
│       │   │   └── course-generate.md
│       │   └── developer/
│       │       ├── test-run.md
│       │       └── lint.md
│       └── designer/                   # Memes skills/agents que profil project
│           ├── skills/ (3)
│           └── agents/ (2)
│
├── shared/                             # Ressources partagees (copiees dans tous les profils)
│   └── references/
│       ├── coding_standards.md
│       └── streamtex_cheatsheet_en.md
│
└── .github/
    └── workflows/
        └── validate.yml                # Verifie que les profils sont complets
```

### 6.3 Format `manifest.toml`

Chaque profil a un `manifest.toml` qui declare son contenu :

```toml
# profiles/project/manifest.toml
[profile]
name = "project"
description = "Standard StreamTeX project development"
extends = ""  # Pas de parent

[commands]
# Categorie = liste de fichiers
designer = [
    "block-new.md", "block-preview.md", "slide-audit.md",
    "slide-fix.md", "slide-new.md", "style-audit.md", "style-refactor.md"
]
migration = [
    "conversion-audit.md", "html-convert-batch.md", "html-convert-block.md",
    "html-export.md", "html-migrate.md"
]
project = ["course-generate.md", "project-upgrade.md", "collection-new.md"]
developer = ["test-run.md", "lint.md"]

[skills]
designer = ["visual-design-rules.md", "style-conventions.md", "streamtex-quick-reference.md"]
developer = ["testing-patterns.md"]

[agents]
designer = ["slide-designer.md", "slide-reviewer.md"]

[shared]
references = ["coding_standards.md", "streamtex_cheatsheet_en.md"]
```

```toml
# profiles/presentation/manifest.toml
[profile]
name = "presentation"
description = "Live projection presentations (10-20m distance)"
extends = "project"  # Herite tout du profil project

# Seulement les ajouts par rapport au parent
[commands]
designer = ["presentation-audit.md", "presentation-fix.md", "survey-convert.md"]

[skills]
designer_ros = ["presentation-design-rules.md", "survey-chart-conversion.md"]

[agents]
designer_ros = ["presentation-designer.md"]
```

### 6.4 Template `CLAUDE.md.j2` (profil project)

```jinja2
# {{ project_name }} — Claude Code Rules

## Identity
You are a **StreamTeX Expert**. You NEVER write standard Streamlit code for content rendering.
You ALWAYS use the `streamtex` library (`stx.*` functions) instead of raw `st.*` calls.

## Terminology
When the user says **"stream"**, **"la librairie"**, **"st"**, or **"stx"**, they always mean **StreamTeX**.

## Environment
- **ALWAYS** prefix Python commands with `uv run` (e.g. `uv run pytest`, `uv run streamlit run ...`)
- **NEVER** call `python`, `pip`, `pytest`, `streamlit`, or `ruff` directly

## Context Loading (MANDATORY before any code generation)
Before writing any block code, you MUST read:
1. `.claude/references/coding_standards.md` — full coding standards
2. `.claude/references/streamtex_cheatsheet_en.md` — syntax reference
3. `book.py` — to understand how blocks are wired

## Coding Standards
- **stx for content, st for interactivity only**
- **One `st_write()` with tuples for inline mixed-style text**
- **No raw HTML/CSS** — use Style composition
- **No hardcoded black/white** — let Streamlit handle themes
- **Block files** need `BlockStyles` class + `build()` function
- **After every code change**: run `uv run ruff check` before committing

{% if profile == "presentation" %}
## Presentation Design (Live Projection)
- Body font: **48pt minimum** (projection distance 10-20m)
- Section titles: **80-96pt**
- Content: **5-7 words/bullet**, 3 max per section
- Helper boxes: **Forbidden** (direct st_write only)
- See `.claude/designer/ros_designer_default/skills/presentation-design-rules.md`
{% endif %}

## Running the App
```bash
uv run streamlit run book.py
```

## Project Structure
```
{{ project_name }}/
├── book.py                 # Entry point
├── blocks/                 # Block files (bck_*.py)
│   ├── __init__.py         # ProjectBlockRegistry
│   └── helpers.py          # Block helper config
├── custom/
│   ├── styles.py           # Project styles
│   └── themes.py           # Theme overrides
├── static/images/          # Static assets
└── .streamlit/config.toml  # Streamlit config
```
```

### 6.5 Script `install.py`

```python
#!/usr/bin/env python3
"""Install a StreamTeX Claude AI profile into a project directory.

Usage:
    python install.py <profile> [target_dir]
    python install.py project ./my-project
    python install.py presentation ./my-presentation
    python install.py library ./streamtex
    python install.py documentation ./streamtex-docs
"""
import argparse
import shutil
import tomllib
from pathlib import Path
from jinja2 import Environment, FileSystemLoader

PROFILES_DIR = Path(__file__).parent / "profiles"
SHARED_DIR = Path(__file__).parent / "shared"

def install_profile(profile_name: str, target_dir: Path, project_name: str = ""):
    profile_dir = PROFILES_DIR / profile_name
    manifest_path = profile_dir / "manifest.toml"

    if not manifest_path.exists():
        print(f"Error: Profile '{profile_name}' not found")
        return False

    with open(manifest_path, "rb") as f:
        manifest = tomllib.load(f)

    target_claude = target_dir / ".claude"
    target_claude.mkdir(parents=True, exist_ok=True)

    # Si le profil etend un autre, installer le parent d'abord
    extends = manifest.get("profile", {}).get("extends", "")
    if extends:
        install_profile(extends, target_dir, project_name)
        # Puis overlay les fichiers supplementaires
        overlay_dir = profile_dir / "overlay"
        if overlay_dir.exists():
            _copy_tree(overlay_dir, target_claude)
    else:
        # Copier les fichiers du profil
        for category in ["commands", "skills", "agents"]:
            if category in manifest:
                for subdir, files in manifest[category].items():
                    src_dir = profile_dir / _resolve_category_path(category, subdir)
                    dst_dir = target_claude / _resolve_category_path(category, subdir)
                    dst_dir.mkdir(parents=True, exist_ok=True)
                    for f in files:
                        shutil.copy2(src_dir / f, dst_dir / f)

    # Copier les ressources partagees
    if "shared" in manifest:
        for subdir, files in manifest["shared"].items():
            src_dir = SHARED_DIR / subdir
            dst_dir = target_claude / subdir
            dst_dir.mkdir(parents=True, exist_ok=True)
            for f in files:
                shutil.copy2(src_dir / f, dst_dir / f)

    # Copier settings.json
    settings_src = profile_dir / "settings.json"
    if settings_src.exists():
        shutil.copy2(settings_src, target_claude / "settings.json")

    # Generer CLAUDE.md depuis le template
    template_path = profile_dir / "CLAUDE.md.j2"
    if not template_path.exists() and extends:
        template_path = PROFILES_DIR / extends / "CLAUDE.md.j2"
    if template_path.exists():
        env = Environment(loader=FileSystemLoader(template_path.parent))
        template = env.get_template(template_path.name)
        claude_md = template.render(
            project_name=project_name or target_dir.name,
            profile=profile_name,
        )
        (target_dir / "CLAUDE.md").write_text(claude_md)

    # Marquer le profil installe
    (target_claude / ".stx-profile").write_text(profile_name)

    print(f"Installed profile '{profile_name}' in {target_dir}")
    return True
```

### 6.6 Migration des fichiers actuels

| Fichier actuel (.claude/) | Profil(s) cible(s) |
|---------------------------|---------------------|
| `commands/designer/block-new.md` | project, documentation |
| `commands/designer/block-preview.md` | project, documentation |
| `commands/designer/slide-audit.md` | project, documentation |
| `commands/designer/slide-fix.md` | project, documentation |
| `commands/designer/slide-new.md` | project, documentation |
| `commands/designer/style-audit.md` | project, documentation |
| `commands/designer/style-refactor.md` | project, documentation |
| `commands/designer/presentation-audit.md` | presentation (overlay) |
| `commands/designer/presentation-fix.md` | presentation (overlay) |
| `commands/designer/survey-convert.md` | presentation (overlay) |
| `commands/developer/test-run.md` | project, library, documentation |
| `commands/developer/lint.md` | project, library, documentation |
| `commands/developer/deploy.md` | library |
| `commands/migration/conversion-audit.md` | project |
| `commands/migration/html-convert-batch.md` | project |
| `commands/migration/html-convert-block.md` | project |
| `commands/migration/html-export.md` | project |
| `commands/migration/html-migrate.md` | project |
| `commands/project/project-new.md` | project |
| `commands/project/collection-new.md` | project |
| `commands/project/project-upgrade.md` | project |
| `commands/project/course-generate.md` | project, documentation |
| `designer/skills/visual-design-rules.md` | project, documentation |
| `designer/skills/style-conventions.md` | project, documentation |
| `designer/skills/streamtex-quick-reference.md` | project, documentation |
| `designer/agents/slide-designer.md` | project, documentation |
| `designer/agents/slide-reviewer.md` | project, documentation |
| `designer/ros_designer_default/skills/presentation-design-rules.md` | presentation (overlay) |
| `designer/ros_designer_default/skills/survey-chart-conversion.md` | presentation (overlay) |
| `designer/ros_designer_default/agents/presentation-designer.md` | presentation (overlay) |
| `developer/skills/architecture.md` | library |
| `developer/skills/testing-patterns.md` | project, library |

---

## 7. Phase 3 : Separation repo `streamtex-docs` — DONE (2026-03-02, commit 1cf89a6)

### 7.1 Objectif

Creer un repo independant pour les manuels, deployable seul sur Render.

### 7.2 Structure cible

```
streamtex-docs/
├── manuals/
│   ├── stx_manual_intro/
│   │   ├── book.py
│   │   ├── setup.py                    # ← MODIFIE : plus de sys.path hack
│   │   ├── blocks/
│   │   ├── custom/
│   │   ├── static/
│   │   └── .streamlit/config.toml
│   ├── stx_manual_advanced/
│   ├── stx_manual_deploy/
│   ├── stx_manuals_collection/
│   │   ├── collection.toml             # URLs Render mises a jour
│   │   └── ...
│   └── shared-blocks/
│       ├── blocks/
│       ├── custom/
│       └── static/
│
├── references/
│   ├── coding_standards.md
│   ├── streamtex_cheatsheet_en.md
│   └── streamtex_cheatsheet_fr.md
│
├── templates/
│   ├── template_project/
│   └── template_collection/
│
├── .claude/                            # Profil "documentation" (installe depuis streamtex-claude)
├── CLAUDE.md
│
├── pyproject.toml
├── uv.lock
├── Dockerfile
├── render.yaml
├── run-manuals.sh
└── .github/workflows/
    └── ci.yml
```

### 7.3 `pyproject.toml` du repo docs

```toml
[project]
name = "streamtex-docs"
version = "0.3.0"
description = "StreamTeX interactive manuals and documentation"
requires-python = ">=3.10"
license = {text = "MIT"}
dependencies = [
    "streamtex>=0.3.0",
]

[dependency-groups]
dev = [
    "pytest>=7.0",
    "ruff>=0.4.0",
]

[tool.uv]
default-groups = ["dev"]

# Override pour dev local — pointe vers le repo librairie adjacent
[tool.uv.sources]
streamtex = { path = "../streamtex", editable = true }
```

### 7.4 Nouveau `setup.py` (sans hack sys.path)

L'ancien `setup.py` dans chaque manuel contenait un hack `sys.path`. Le nouveau :

```python
"""StreamTeX project setup — configures import paths."""
import sys
from pathlib import Path

# Le package streamtex est installe via pip/uv (plus de sys.path hack)
# On ajoute seulement le dossier parent pour les imports locaux (shared-blocks, etc.)
PROJECT_DIR = Path(__file__).resolve().parent
MANUALS_DIR = PROJECT_DIR.parent

# Ajouter le dossier shared-blocks pour les imports inter-manuels
SHARED_BLOCKS_DIR = MANUALS_DIR / "shared-blocks"
if SHARED_BLOCKS_DIR.exists() and str(SHARED_BLOCKS_DIR) not in sys.path:
    sys.path.insert(0, str(SHARED_BLOCKS_DIR))
```

### 7.5 Dockerfile du repo docs

```dockerfile
FROM python:3.13-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 \
    STREAMLIT_SERVER_HEADLESS=true UV_LINK_MODE=copy
WORKDIR /app
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev
# streamtex est installe depuis PyPI via uv sync ↑

ARG FOLDER="manuals/stx_manual_intro"
COPY manuals/ ./manuals/
# On copie tout manuals/ car shared-blocks est necessaire

WORKDIR /app/${FOLDER}
EXPOSE 8501
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health
ENTRYPOINT ["uv", "run", "streamlit", "run", "book.py", \
            "--server.port=8501", "--server.address=0.0.0.0"]
```

**Difference avec l'ancien Dockerfile** : Plus besoin de `COPY streamtex/ ./streamtex/` — la librairie vient de PyPI.

### 7.6 `render.yaml` du repo docs

```yaml
services:
  - type: web
    name: streamtex
    runtime: docker
    repo: https://github.com/nicolasguelfi/streamtex-docs
    branch: main
    plan: free
    dockerfilePath: ./Dockerfile
    dockerContext: .
    envVars:
      - key: FOLDER
        value: manuals/stx_manuals_collection
      - key: STX_URL_TEST_INTRO
        value: https://streamtex-intro.onrender.com
      - key: STX_URL_TEST_ADVANCED
        value: https://streamtex-advanced.onrender.com
      - key: STX_URL_TEST_DEPLOY
        value: https://streamtex-deploy.onrender.com
      - key: STX_PASSWORD
        value: changeme
    healthCheckPath: /_stcore/health

  - type: web
    name: streamtex-intro
    runtime: docker
    repo: https://github.com/nicolasguelfi/streamtex-docs
    branch: main
    plan: free
    dockerfilePath: ./Dockerfile
    dockerContext: .
    envVars:
      - key: FOLDER
        value: manuals/stx_manual_intro
      - key: STX_PASSWORD
        value: changeme
    healthCheckPath: /_stcore/health

  - type: web
    name: streamtex-advanced
    runtime: docker
    repo: https://github.com/nicolasguelfi/streamtex-docs
    branch: main
    plan: free
    dockerfilePath: ./Dockerfile
    dockerContext: .
    envVars:
      - key: FOLDER
        value: manuals/stx_manual_advanced
      - key: STX_PASSWORD
        value: changeme
    healthCheckPath: /_stcore/health

  - type: web
    name: streamtex-deploy
    runtime: docker
    repo: https://github.com/nicolasguelfi/streamtex-docs
    branch: main
    plan: free
    dockerfilePath: ./Dockerfile
    dockerContext: .
    envVars:
      - key: FOLDER
        value: manuals/stx_manual_deploy
      - key: STX_PASSWORD
        value: changeme
    healthCheckPath: /_stcore/health
```

### 7.7 Migration de l'historique Git

Utiliser `git-filter-repo` pour extraire les fichiers pertinents avec leur historique :

```bash
# 1. Creer un clone frais du monorepo
git clone https://github.com/nicolasguelfi/streamtex.git /tmp/streamtex-docs-migration
cd /tmp/streamtex-docs-migration

# 2. Extraire les chemins pertinents
git filter-repo \
    --path documentation/manuals/ \
    --path documentation/coding_standards.md \
    --path documentation/streamtex_cheatsheet_en.md \
    --path documentation/streamtex_cheatsheet_fr.md \
    --path documentation/template_project/ \
    --path documentation/template_collection/ \
    --path-rename documentation/manuals/:manuals/ \
    --path-rename documentation/coding_standards.md:references/coding_standards.md \
    --path-rename documentation/streamtex_cheatsheet_en.md:references/streamtex_cheatsheet_en.md \
    --path-rename documentation/streamtex_cheatsheet_fr.md:references/streamtex_cheatsheet_fr.md \
    --path-rename documentation/template_project/:templates/template_project/ \
    --path-rename documentation/template_collection/:templates/template_collection/

# 3. Ajouter le nouveau remote
git remote add origin https://github.com/nicolasguelfi/streamtex-docs.git
git push -u origin main
```

---

## 8. Phase 4 : Autonomisation des projets

### 8.1 Objectif

Rendre chaque projet StreamTeX deployable de maniere independante.

### 8.2 Structure type d'un projet autonome

```
ai4se-streamtex/
├── blocks/
│   ├── __init__.py
│   ├── bck_title.py
│   ├── bck_survey_ai_tools.py
│   └── bck_survey_dev_ides.py
├── custom/
│   ├── __init__.py
│   ├── styles.py
│   └── themes.py
├── static/
│   └── images/
├── book.py
├── setup.py                            # ← SIMPLIFIE : plus de sys.path
├── .streamlit/config.toml
├── .claude/                            # Installe via stx claude install presentation
├── CLAUDE.md                           # Genere depuis template presentation
├── pyproject.toml
├── uv.lock
├── Dockerfile                          # Genere via stx deploy docker --init
├── render.yaml                         # Genere via stx deploy render --init
├── .github/workflows/ci.yml
└── .gitignore
```

### 8.3 `pyproject.toml` type d'un projet

```toml
[project]
name = "ai4se-streamtex"
version = "1.0.0"
description = "AI4SE course materials built with StreamTeX"
requires-python = ">=3.10"
license = {text = "MIT"}
dependencies = [
    "streamtex>=0.3.0",
]

[dependency-groups]
dev = ["pytest>=7.0", "ruff>=0.4.0"]

[tool.uv]
default-groups = ["dev"]

# Dev local seulement — ignore par pip
[tool.uv.sources]
streamtex = { path = "../../streamtex", editable = true }
```

### 8.4 Nouveau `setup.py` simplifie

```python
"""Project setup — streamtex installed via pip, no sys.path hack needed."""
# Ce fichier est conserve par convention mais n'a plus besoin
# de manipuler sys.path puisque streamtex est un package installe.
```

### 8.5 Procedure de migration par projet

Pour chaque projet (AI4SE, AIAI18H, MODELSWARD) :

```bash
# 1. Creer le repo GitHub
gh repo create nicolasguelfi/ai4se-streamtex --public

# 2. Copier les fichiers du projet (pas d'historique git a migrer pour les projets)
mkdir /tmp/ai4se-migration
cp -r projects/AI4SE/* /tmp/ai4se-migration/

# 3. Initialiser le nouveau repo
cd /tmp/ai4se-migration
git init
git remote add origin https://github.com/nicolasguelfi/ai4se-streamtex.git

# 4. Ajouter les fichiers d'infrastructure
# → pyproject.toml, Dockerfile, render.yaml, .gitignore, CI/CD

# 5. Installer le profil Claude
cd ~/dev/streamtex-dev/streamtex-claude
python install.py presentation /tmp/ai4se-migration

# 6. Premier commit + push
cd /tmp/ai4se-migration
git add .
git commit -m "Initial commit: AI4SE StreamTeX project"
git push -u origin main

# 7. Cloner dans le workspace
cd ~/dev/streamtex-dev/projects
git clone https://github.com/nicolasguelfi/ai4se-streamtex.git

# 8. Configurer editable install
cd ai4se-streamtex
uv sync  # Utilise [tool.uv.sources] pour streamtex editable
```

### 8.6 Analyse quota Render (tier gratuit)

| Service | Type | Repo | Impact quota |
|---------|------|------|-------------|
| `streamtex` (collection) | Docs | streamtex-docs | ~50h/mois (sleep 15min) |
| `streamtex-intro` | Docs | streamtex-docs | ~50h/mois |
| `streamtex-advanced` | Docs | streamtex-docs | ~50h/mois |
| `streamtex-deploy` | Docs | streamtex-docs | ~50h/mois |
| `ai4se-streamtex` | Projet | ai4se-streamtex | ~50h/mois |
| **Total** | | | **~250h/mois** |
| **Quota gratuit** | | | **750h/mois** |
| **Marge** | | | **~500h/mois** |

Avec le free tier et le sleep a 15 minutes, 5 services consomment environ 250h/mois, bien sous le quota de 750h.

---

## 9. Phase 5 : Nettoyage du repo librairie — DONE (2026-03-02, commit 7fd7d4f)

### 9.1 Objectif

Reduire le repo `streamtex` a la librairie, aux tests, et au CLI.

### 9.2 Fichiers a GARDER dans le repo librairie

```
streamtex/
├── streamtex/                  # Package Python (37 modules + styles/ + static/ + cli/)
├── tests/                      # 19 fichiers de test
├── .claude/                    # Profil "library" (installe depuis streamtex-claude)
├── .github/
│   └── workflows/
│       ├── ci.yml              # Tests + lint
│       └── publish.yml         # PyPI Trusted Publishing
├── CLAUDE.md                   # Genere depuis profil library
├── pyproject.toml              # Package PyPI + CLI entry point
├── uv.lock
├── README.md                   # Oriente utilisateur (PyPI)
├── CHANGELOG.md                # Historique des versions
├── LICENSE                     # MIT
└── .gitignore
```

### 9.3 Fichiers a SUPPRIMER du repo librairie (deja migres)

```
# Migration vers streamtex-docs
documentation/manuals/          → streamtex-docs/manuals/
documentation/coding_standards.md → streamtex-docs/references/ + streamtex-claude/shared/
documentation/streamtex_cheatsheet_*.md → idem
documentation/template_project/ → streamtex-docs/templates/
documentation/template_collection/ → streamtex-docs/templates/
documentation/architecture_collections_multirepo.md → archive

# Migration vers streamtex-claude
.claude/commands/designer/      → streamtex-claude/profiles/
.claude/commands/migration/     → streamtex-claude/profiles/
.claude/commands/project/       → streamtex-claude/profiles/
.claude/designer/               → streamtex-claude/profiles/

# Migration vers repos projets
projects/AI4SE/                 → ai4se-streamtex/
projects/project_aiai18h/       → aiai18h-streamtex/
projects/project_modelsward/    → modelsward-streamtex/
projects/project_html_example/  → archive ou repo dedie

# Suppression (plus necessaire en multi-repo)
docker-compose.yml              # Chaque repo a le sien
render.yaml                     # Chaque repo a le sien
run-test-projects.sh            # Remplace par stx workspace
deploy/                         # Integre dans stx CLI + chaque repo
collection.toml                 # Specifique au repo docs
```

### 9.4 Fichiers a GARDER/ADAPTER dans le repo librairie

| Fichier | Action |
|---------|--------|
| `Dockerfile` | Garder comme template reference (utilise par stx deploy) |
| `.github/workflows/ci.yml` | Adapter (supprimer Docker build, garder tests+lint) |
| `documentation/maintenance/` | Garder comme archive historique |
| `.claude/commands/developer/` | Garder (profil library) |
| `.claude/developer/skills/` | Garder (profil library) |
| `.claude/settings.json` | Adapter pour le repo librairie |

### 9.5 `.claude/` du repo librairie apres nettoyage

```
streamtex/.claude/
├── settings.json
├── commands/
│   └── developer/
│       ├── test-run.md
│       ├── lint.md
│       └── deploy.md
└── developer/
    └── skills/
        ├── architecture.md
        └── testing-patterns.md
```

---

## 10. Phase 6 : Script CLI `stx` et workspace

### 10.1 Objectif

Implementer le CLI `stx` decrit en section 4.

### 10.2 Dependances du CLI

```toml
# Dans pyproject.toml [project.optional-dependencies]
cli = [
    "click>=8.0",       # Framework CLI
    "rich>=13.0",       # Output console riche (tables, couleurs, spinners)
    "jinja2>=3.0",      # Templates pour CLAUDE.md, Dockerfile, etc.
    "tomli>=2.0;python_version<'3.11'",  # TOML parsing (stdlib en 3.11+)
]
```

### 10.3 Plan d'implementation

| Etape | Commandes | Effort | Priorite |
|-------|-----------|--------|----------|
| 1 | `stx workspace init/clone/status` | 1 session | **DONE** |
| 2 | `stx claude install/list` | 1 session | **DONE** |
| 3 | `stx project new/validate` | 1 session | **DONE** |
| 4 | `stx deploy preflight/docker` | 1 session | **DONE** |
| 5 | `stx deploy render` | 1 session | **DONE** |
| 6 | `stx deploy huggingface` | 1 session | **DONE** |
| 7 | `stx publish check/pypi` | 0.5 session | **DONE** |
| 8 | `stx workspace link/sync` | 0.5 session | **DONE** |
| 9 | `stx deploy status` | 0.5 session | **DONE** |
| 10 | `stx claude update/diff` | 0.5 session | **DONE** |

### 10.4 Tests du CLI

Chaque commande aura ses tests dans `tests/test_cli_*.py` :

```python
# tests/test_cli_workspace.py
def test_workspace_init(tmp_path):
    """stx workspace init creates stx.toml with correct structure."""
    from streamtex.cli.workspace import init_workspace
    init_workspace(tmp_path)
    config_path = tmp_path / "stx.toml"
    assert config_path.exists()
    # Verify TOML content...

# tests/test_cli_deploy.py
def test_preflight_missing_book(tmp_path):
    """Preflight fails if book.py is missing."""
    from streamtex.cli.deploy.preflight import run_preflight
    result = run_preflight(tmp_path)
    assert not result.success
    assert "book.py" in result.errors[0]
```

---

## 11. Matrice des risques

| # | Risque | Probabilite | Impact | Mitigation |
|---|--------|-------------|--------|------------|
| R1 | Nom `streamtex` pris sur PyPI avant publication | Faible | Critique | Publier Phase 1 en priorite, nom verifie dispo 2026-02-25 |
| R2 | Imports casses apres suppression sys.path hack | Moyenne | Majeur | Tester chaque manual/projet avant de supprimer le monorepo |
| R3 | Perte d'historique Git lors de la separation | Faible | Mineur | Utiliser git-filter-repo (preserve l'historique) |
| R4 | Downtime Render pendant la migration | Moyenne | Mineur | Migrer un service a la fois, garder l'ancien en parallele |
| R5 | Depassement quota Render (750h/mois) | Faible | Mineur | 5 services ≈ 250h/mois, marge confortable |
| R6 | Profils Claude desynchronises entre projets | Moyenne | Mineur | `stx claude update` + CI qui valide les profils |
| R7 | `[tool.uv.sources]` casse pour Bob (pas de repo lib local) | Faible | Majeur | Bob n'a PAS cette section — elle est specifique au workspace Nicolas |
| R8 | Shared blocks cassent en multi-repo | Moyenne | Majeur | Tester avec streamtex depuis PyPI, pas editable |
| R9 | CLI `stx` ajoute complexite pour Bob | Faible | Mineur | Bob n'a pas besoin du CLI — il peut utiliser directement pip + Claude |
| R10 | Templates Jinja2 dans CLAUDE.md cassent la syntaxe | Faible | Mineur | Tests automatises de generation des templates |

---

## 12. Calendrier recommande

```
Phase 1: PyPI              ████████████████  DONE (2026-03-01, commit c7d6d8d)
Phase 2: streamtex-claude  ████████████████  DONE (2026-03-01)
Phase 3: streamtex-docs    ████████████████  DONE (2026-03-02, commit 1cf89a6)
Phase 4: Projets           ████████████████  DONE (2026-03-02)
Phase 5: Nettoyage lib     ████████████████  DONE (2026-03-02, commit 7fd7d4f)
Phase 6: CLI stx           ████████████████  Continu (incremental, 4-6 sessions total)
```

**Ordre obligatoire** :
- Phase 1 (PyPI) **DOIT** etre terminee avant Phases 3 et 4
- Phase 2 (Claude) **PEUT** etre faite en parallele de Phase 1
- Phase 3 (Docs) et Phase 4 (Projets) **PEUVENT** etre paralleles
- Phase 5 (Nettoyage) **DOIT** etre derniere
- Phase 6 (CLI) est incrementale et peut demarrer des Phase 1

**Estimation totale** : 8-12 sessions de travail

---

## Annexe A : Mapping fichiers actuel → cible

### A.1 Fichiers du monorepo → Repo librairie (`streamtex`)

| Source (monorepo) | Destination | Action |
|-------------------|-------------|--------|
| `streamtex/` | `streamtex/` | Garder tel quel |
| `tests/` | `tests/` | Garder tel quel |
| `pyproject.toml` | `pyproject.toml` | Modifier (ajouter classifiers, URLs, CLI entry) |
| `.github/workflows/ci.yml` | `.github/workflows/ci.yml` | Simplifier (retirer Docker) |
| `.gitignore` | `.gitignore` | Garder |
| `documentation/maintenance/` | `documentation/maintenance/` | Garder comme archive |
| `.claude/commands/developer/` | `.claude/commands/developer/` | Garder |
| `.claude/developer/skills/` | `.claude/developer/skills/` | Garder |
| `CLAUDE.md` | `CLAUDE.md` | Reecrire (profil library) |

### A.2 Fichiers du monorepo → Repo docs (`streamtex-docs`)

| Source (monorepo) | Destination | Action |
|-------------------|-------------|--------|
| `documentation/manuals/stx_manual_intro/` | `manuals/stx_manual_intro/` | Migrer + modifier setup.py |
| `documentation/manuals/stx_manual_advanced/` | `manuals/stx_manual_advanced/` | Migrer + modifier setup.py |
| `documentation/manuals/stx_manual_deploy/` | `manuals/stx_manual_deploy/` | Migrer + modifier setup.py |
| `documentation/manuals/stx_manuals_collection/` | `manuals/stx_manuals_collection/` | Migrer + maj collection.toml |
| `documentation/manuals/stx_manuals_shared-blocks/` | `manuals/shared-blocks/` | Migrer |
| `documentation/coding_standards.md` | `references/coding_standards.md` | Copier |
| `documentation/streamtex_cheatsheet_en.md` | `references/streamtex_cheatsheet_en.md` | Copier |
| `documentation/streamtex_cheatsheet_fr.md` | `references/streamtex_cheatsheet_fr.md` | Copier |
| `documentation/template_project/` | `templates/template_project/` | Migrer |
| `documentation/template_collection/` | `templates/template_collection/` | Migrer |
| `render.yaml` | `render.yaml` | Reecrire (pointe vers streamtex-docs) |
| `Dockerfile` | `Dockerfile` | Simplifier (plus de COPY streamtex/) |
| `docker-compose.yml` | `docker-compose.yml` | Adapter chemins |

### A.3 Fichiers du monorepo → Repo Claude (`streamtex-claude`)

| Source (monorepo) | Destination | Action |
|-------------------|-------------|--------|
| `.claude/commands/designer/*.md` (7) | `profiles/project/commands/designer/` | Copier |
| `.claude/commands/migration/*.md` (5) | `profiles/project/commands/migration/` | Copier |
| `.claude/commands/project/*.md` (4) | `profiles/project/commands/project/` | Copier |
| `.claude/commands/developer/test-run.md` | Plusieurs profils | Copier |
| `.claude/commands/developer/lint.md` | Plusieurs profils | Copier |
| `.claude/commands/developer/deploy.md` | `profiles/library/commands/developer/` | Copier |
| `.claude/designer/skills/*.md` (3) | `profiles/project/designer/skills/` | Copier |
| `.claude/designer/agents/*.md` (2) | `profiles/project/designer/agents/` | Copier |
| `.claude/designer/ros_designer_default/` | `profiles/presentation/overlay/designer/` | Copier |
| `.claude/developer/skills/*.md` (2) | `profiles/library/developer/skills/` | Copier |
| `documentation/coding_standards.md` | `shared/references/` | Copier |
| `documentation/streamtex_cheatsheet_en.md` | `shared/references/` | Copier |

### A.4 Fichiers du monorepo → Repos projets

| Source (monorepo) | Destination | Action |
|-------------------|-------------|--------|
| `projects/AI4SE/` | `ai4se-streamtex/` | Copier + ajouter infra |
| `projects/AI4SE/CLAUDE.md` | (regenere depuis profil presentation) | Regenerer |
| `projects/project_aiai18h/` | `aiai18h-streamtex/` | Copier + ajouter infra |
| `projects/project_modelsward/` | `modelsward-streamtex/` | Copier + ajouter infra |

### A.5 Fichiers a archiver/supprimer

| Fichier | Action |
|---------|--------|
| `projects/AIDAY/` | Archiver (notes personnelles, pas un projet STX) |
| `projects/modelsward/` | Archiver (materiaux, pas un projet STX) |
| `projects/project_html_example/` | Archiver ou migrer si utile |
| `projects/convert_html_to_streamtex/` | Garder dans monorepo temporairement ou repo dedie |
| `documentation/architecture_collections_multirepo.md` | Archiver dans maintenance/ |
| `documentation/notes.txt` | Archiver |
| `collection.toml` (racine) | Supprimer (deplace dans streamtex-docs) |
| `run-test-projects.sh` | Supprimer (remplace par stx workspace) |
| `deploy/` | Integre dans stx CLI |

---

## Annexe B : Profils Claude AI — Contenu detaille

### B.1 Profil `project` — Pour Bob (dev projet standard)

**Identite Claude** : StreamTeX Expert — aide a creer des projets
**CLAUDE.md** : Focus sur la creation de blocs, styles, deploiement
**Commandes** : 17 slash commands

| Categorie | Commandes | Usage |
|-----------|-----------|-------|
| designer | block-new, block-preview, slide-audit, slide-fix, slide-new, style-audit, style-refactor | Creation et audit de blocs |
| migration | conversion-audit, html-convert-batch, html-convert-block, html-export, html-migrate | Migration HTML |
| project | course-generate, project-upgrade, collection-new | Gestion projet |
| developer | test-run, lint | Qualite code |

**Skills** : 4 knowledge files

| Skill | Contenu |
|-------|---------|
| visual-design-rules | Regles de design visuel (fonts, couleurs, espacement) |
| style-conventions | Conventions de nommage et patterns de styles |
| streamtex-quick-reference | Reference rapide API StreamTeX |
| testing-patterns | Patterns de test (utile pour les projets aussi) |

**Agents** : 2 agents
- `slide-designer` : Creation de slides
- `slide-reviewer` : Review de slides

### B.2 Profil `presentation` — Extensions pour projection live

**Etend** : Profil `project` (herite tout)
**Ajouts** :

| Type | Fichier | Contenu |
|------|---------|---------|
| Commande | presentation-audit | Audit pour projection live |
| Commande | presentation-fix | Fix auto des violations projection |
| Commande | survey-convert | Conversion screenshots survey |
| Skill | presentation-design-rules | 9 regles de projection (48pt min, etc.) |
| Skill | survey-chart-conversion | Regles conversion graphiques |
| Agent | presentation-designer | Role de designer presentations |

**Override CLAUDE.md** : Ajoute une section "Presentation Design" avec les contraintes de projection.

### B.3 Profil `library` — Pour Nicolas (dev librairie)

**Identite Claude** : StreamTeX Library Developer
**CLAUDE.md** : Focus sur l'architecture interne, tests, PyPI
**Commandes** : 3 slash commands

| Commande | Usage |
|----------|-------|
| test-run | Executer les tests |
| lint | Linting ruff |
| deploy | Deploiement (Docker, PyPI) |

**Skills** : 2 knowledge files

| Skill | Contenu |
|-------|---------|
| architecture | Graphe de dependances modules, design patterns, testing strategy |
| testing-patterns | Patterns de test, fixtures, mocking, AST guard |

### B.4 Profil `documentation` — Pour Nicolas (dev manuels)

**Identite Claude** : StreamTeX Documentation Author
**CLAUDE.md** : Focus sur la creation de manuels interactifs
**Commandes** : 10 slash commands (subset de project + course-generate)

| Categorie | Commandes |
|-----------|-----------|
| designer | block-new, block-preview, slide-audit, slide-fix, slide-new, style-audit, style-refactor |
| project | course-generate |
| developer | test-run, lint |

**Skills et Agents** : Memes que le profil `project` (designer skills + agents)

---

## Annexe C : Templates de fichiers cles

### C.1 `.gitignore` commun a tous les repos

```gitignore
# Python
__pycache__/
*.py[cod]
*$py.class
*.egg-info/
dist/
build/
.eggs/

# Virtual environments
.venv/
venv/
ENV/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Streamlit
.streamlit/secrets.toml

# Environment
.env
.env.local

# uv
uv.lock  # ← Inclure dans .gitignore si repo projet Bob ; EXCLURE si repo lib Nicolas

# Claude Code
.claude/memory/
```

### C.2 `ci.yml` template pour les repos projets

```yaml
name: CI
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  validate:
    name: Validate Project
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
        with: { enable-cache: true }
      - run: uv python install
      - run: uv sync --frozen
      - run: uv run python -c "from streamtex import st_write; print('StreamTeX import OK')"

  docker:
    name: Docker Build
    runs-on: ubuntu-latest
    needs: validate
    if: github.event_name == 'push'
    steps:
      - uses: actions/checkout@v4
      - run: docker build -t ${{ github.event.repository.name }} .
      - run: |
          docker run -d --name test -p 8501:8501 ${{ github.event.repository.name }}
          sleep 10
          curl --fail --retry 5 --retry-delay 3 http://localhost:8501/_stcore/health
          docker stop test
```

---

## Annexe D : Checklist de validation par phase

### D.1 Phase 1 — Publication PyPI (DONE 2026-03-01)

- [x] `pyproject.toml` enrichi (classifiers, URLs, authors, version 0.3.0)
- [x] `README.md` oriente utilisateur cree
- [x] `CHANGELOG.md` cree
- [x] `LICENSE` MIT cree
- [x] `__version__ = "0.3.0"` dans `streamtex/__init__.py`
- [x] `streamlit-ace` deplace vers `[project.optional-dependencies].inspector`
- [x] `.github/workflows/publish.yml` cree
- [x] Trusted Publishing configure sur PyPI
- [x] Publication TestPyPI reussie
- [x] Installation depuis TestPyPI validee : `pip install streamtex==0.3.0`
- [x] Tag `v0.3.0` pousse
- [x] Release GitHub creee → publish.yml declenche
- [x] Publication PyPI production reussie
- [x] `pip install streamtex` fonctionne dans un venv vierge

### D.2 Phase 2 — Repo `streamtex-claude` (DONE 2026-03-01)

- [x] Repo GitHub `nicolasguelfi/streamtex-claude` cree
- [x] Structure `profiles/` avec 4 profils
- [x] `manifest.toml` pour chaque profil
- [x] `CLAUDE.md.j2` template pour chaque profil
- [x] `settings.json` pour chaque profil
- [x] `shared/references/` avec coding_standards + cheatsheet
- [x] `install.py` fonctionnel
- [x] Test : `python install.py project /tmp/test-project` → `.claude/` complet
- [x] Test : `python install.py presentation /tmp/test-pres` → profil project + overlay
- [x] Test : `python install.py library /tmp/test-lib` → profil minimal
- [x] Test : Claude Code fonctionne dans un projet avec profil installe
- [x] `README.md` avec instructions d'utilisation

### D.3 Phase 3 — Repo `streamtex-docs` (DONE 2026-03-02)

- [x] Repo GitHub `nicolasguelfi/streamtex-docs` cree
- [x] Historique Git migre avec `git-filter-repo` (105 commits preserves, LFS inclus)
- [x] `pyproject.toml` avec `streamtex>=0.3.0`
- [x] `[tool.uv.sources]` pour dev local (editable `../streamtex`)
- [x] `setup.py` de chaque manual mis a jour (shared-blocks cross-import)
- [x] `uv sync` fonctionne (installe streamtex 0.3.0 editable)
- [ ] `uv run streamlit run manuals/stx_manual_intro/book.py` fonctionne
- [ ] `uv run streamlit run manuals/stx_manual_advanced/book.py` fonctionne
- [ ] `uv run streamlit run manuals/stx_manual_deploy/book.py` fonctionne
- [ ] `uv run streamlit run manuals/stx_manuals_collection/book.py` fonctionne
- [x] Profil Claude "documentation" installe et fonctionnel (19 fichiers)
- [x] `Dockerfile` simplifie (streamtex via PyPI)
- [x] `render.yaml` pointe vers le nouveau repo
- [ ] Docker build + health check passent localement
- [ ] Services Render migres un par un (ancien → nouveau repo)
- [ ] Tous les services Render fonctionnels

### D.4 Phase 4 — Projets autonomes

Pour chaque projet (AI4SE, AIAI18H, MODELSWARD) :

- [ ] Repo GitHub cree
- [ ] Fichiers projet copies
- [ ] `pyproject.toml` cree avec `streamtex>=0.3.0`
- [ ] `setup.py` simplifie
- [ ] Profil Claude installe (presentation pour AI4SE, project pour les autres)
- [ ] `CLAUDE.md` genere
- [ ] `Dockerfile` genere
- [ ] `.github/workflows/ci.yml` cree
- [ ] `uv sync && uv run streamlit run book.py` fonctionne
- [ ] Docker build + health check passent localement
- [ ] Premier commit + push reussi
- [ ] (Si Render) : `render.yaml` cree et service deploye

### D.5 Phase 5 — Nettoyage librairie (DONE 2026-03-02)

- [x] `projects/` supprime du repo librairie
- [x] `documentation/manuals/` supprime
- [x] `documentation/template_*/` supprime
- [x] `documentation/coding_standards.md` supprime (existe dans streamtex-claude + streamtex-docs)
- [x] `documentation/streamtex_cheatsheet_*.md` supprime (idem)
- [x] `.claude/` reduit au profil "library" (9 fichiers)
- [x] `CLAUDE.md` reecrit pour le profil library
- [x] `docker-compose.yml` supprime
- [x] `render.yaml` (racine) supprime
- [x] `collection.toml` (racine) supprime
- [x] `run-test-projects.sh` supprime
- [x] `deploy/` supprime
- [x] `.cursor/` supprime (regles migrees vers streamtex-claude)
- [x] `ci.yml` simplifie (job Docker build supprime)
- [x] `.gitignore` et `.dockerignore` nettoyes
- [x] Tests passent : `uv run pytest tests/ -v` (917 tests)
- [x] Lint propre : `uv run ruff check streamtex/`
- [x] CI/CD fonctionne

### D.6 Phase 6 — CLI `stx`

- [x] `streamtex/cli/` cree avec structure modulaire
- [x] `[project.scripts] stx = ...` dans pyproject.toml
- [x] `[project.optional-dependencies] cli = [...]` defini
- [x] `stx workspace init` fonctionne
- [x] `stx workspace clone` fonctionne
- [x] `stx workspace link` fonctionne (uv sync dans chaque repo)
- [x] `stx workspace status` affiche l'etat correct
- [x] `stx claude install <profile>` fonctionne
- [x] `stx claude list` affiche les 4 profils
- [x] `stx project new <name>` scaffolde un projet complet
- [x] `stx project validate <path>` detecte les problemes
- [x] `stx deploy preflight` execute tous les checks
- [x] `stx deploy docker` build + run localement
- [x] `stx deploy render` genere render.yaml + guide
- [x] `stx deploy huggingface` configure LFS + README + remote
- [x] `stx publish check` valide la readiness PyPI
- [x] `stx publish pypi --test` publie sur TestPyPI
- [x] Tests CLI : `uv run pytest tests/test_cli_*.py -v`

### D.7 Validation post-migration (globale)

- [ ] Bob peut faire : `pip install streamtex` → creer un projet → deployer
- [ ] Nicolas peut faire : modifier la lib → tester dans les manuels (editable) → publier
- [ ] Nicolas peut faire : `stx workspace status` → voir l'etat de tout
- [ ] Nicolas peut faire : `stx deploy render ./streamtex-docs --multi` → deployer tous les manuels
- [ ] Tous les services Render fonctionnent avec les nouveaux repos
- [ ] Claude Code fonctionne dans chaque repo avec le bon profil
- [ ] CI/CD fonctionne dans chaque repo independamment
- [ ] Aucun repo ne depend d'un hack `sys.path`
