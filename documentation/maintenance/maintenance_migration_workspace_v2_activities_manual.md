# Guide Pratique du Workspace Multi-Repo StreamTeX

> **Pour** : Nicolas (developpeur librairie + docs + projets)
> **Date** : 2026-03-02
> **Reference** : `maintenance_migration_workspace_v2.md`

---

## Vue d'ensemble du workspace

```
~/dev/streamtex-dev/
├── streamtex/              ← Librairie Python (repo git)
├── streamtex-docs/         ← Manuels utilisateur (repo git)
├── streamtex-claude/       ← Profils Claude AI (repo git)
├── projects/
│   ├── stx-ai4se/    ← Projet AI4SE (repo git)
│   ├── stx-aiai18h/  ← Projet AIAI18H (repo git)
│   └── stx-modelsward/
└── stx.toml                ← Config workspace
```

**Principe cle** : Chaque repo a son propre `.claude/` (profil adapte), mais Claude Code
peut lire et modifier des fichiers dans **tout le filesystem**. Les editable installs font
que toute modification de la librairie est **immediatement visible** dans les docs et projets
sans rien republier.

---

## 1. Taches quotidiennes — Ou lancer Claude et quoi faire

### Tache A : Developper la librairie (`streamtex/`)

```
Ou lancer Claude :  ~/dev/streamtex-dev/streamtex/
Profil charge :     library (architecture, testing-patterns, test-run, lint)
```

**Workflow** :
```bash
cd ~/dev/streamtex-dev/streamtex
claude                          # Lance Claude avec le profil library
```

Claude a acces a :
- **streamtex/** — le code source de la librairie (lecture + ecriture)
- **tests/** — les tests unitaires
- **.claude/commands/developer/** — `/developer:test-run`, `/developer:lint`, `/developer:deploy`
- **.claude/developer/skills/** — architecture.md, testing-patterns.md

Commandes disponibles :
- `/developer:test-run` — lancer les 203 tests
- `/developer:lint` — lancer ruff
- `/developer:deploy` — publier (Docker, PyPI)

**Cas concret** : "Ajouter un parametre `align` a `st_list`"
1. Claude lit `streamtex/list.py`, modifie le code
2. Claude lit/modifie les tests dans `tests/test_list.py`
3. `/developer:test-run` pour valider
4. `/developer:lint` pour verifier

---

### Tache B : Developper les manuels (`streamtex-docs/`)

```
Ou lancer Claude :  ~/dev/streamtex-dev/streamtex-docs/
Profil charge :     documentation (designer skills, slide/block commands, test-run, lint)
```

**Workflow** :
```bash
cd ~/dev/streamtex-dev/streamtex-docs
claude
```

Claude a acces a :
- **manuals/** — tous les manuels (intro, advanced, deploy, collection, shared-blocks)
- **references/** — coding_standards.md, cheatsheet
- **templates/** — template_project, template_collection
- **.claude/commands/designer/** — block-new, slide-new, style-audit, etc.
- **.claude/designer/skills/** — visual-design-rules, style-conventions, quick-reference

Commandes disponibles :
- `/designer:block-new` — creer un nouveau bloc
- `/designer:slide-new` — creer un nouveau slide
- `/designer:slide-audit` — auditer un slide
- `/project:course-generate` — generer un book.py depuis blocks.csv
- `/developer:test-run`, `/developer:lint`

**Cas concret** : "Ajouter un bloc sur les overlays dans le manual advanced"
1. Claude lit `references/coding_standards.md` et `references/streamtex_cheatsheet_en.md`
2. `/designer:block-new` dans `manuals/stx_manual_advanced/blocks/_atomic/`
3. Claude ajoute le bloc au `book.py` du manual
4. Tester : `uv run streamlit run manuals/stx_manual_advanced/book.py`

---

### Tache C : Developper un projet (ex: AI4SE)

```
Ou lancer Claude :  ~/dev/streamtex-dev/projects/stx-ai4se/
Profil charge :     presentation (tout le profil project + regles projection live)
```

**Workflow** :
```bash
cd ~/dev/streamtex-dev/projects/stx-ai4se
claude
```

Claude a acces a :
- **blocks/, custom/, static/** — le contenu du projet
- **.claude/commands/designer/** — y compris presentation-audit, presentation-fix
- **.claude/designer/ros_designer_default/** — regles projection 48pt min, etc.
- **.claude/commands/migration/** — pour convertir du HTML si besoin

Commandes disponibles (17+3) :
- Toutes les commandes du profil `project`
- **+** `/designer:presentation-audit`, `/designer:presentation-fix`, `/designer:survey-convert`

**Cas concret** : "Creer un slide sur les outils AI pour les developpeurs"
1. `/designer:slide-new bck_ai_dev_tools`
2. Claude lit les regles de projection (48pt min, 5-7 mots/bullet)
3. `/designer:presentation-audit` pour verifier la conformite

---

### Tache D : Maintenir les profils Claude AI

```
Ou lancer Claude :  ~/dev/streamtex-dev/streamtex-claude/
Profil charge :     aucun specifique (repo utilitaire, pas de profil StreamTeX)
```

**Workflow** :
```bash
cd ~/dev/streamtex-dev/streamtex-claude
claude
```

Claude travaille directement sur les fichiers des profils :
- `profiles/project/`, `profiles/presentation/`, `profiles/library/`, `profiles/documentation/`
- `shared/references/`
- `install.py`, `update.py`

**Cas concret** : "Ajouter une nouvelle commande `/designer:color-palette`"
1. Claude cree `profiles/project/commands/designer/color-palette.md`
2. Claude met a jour `profiles/project/manifest.toml`
3. Claude met a jour aussi `profiles/documentation/manifest.toml` (si pertinent)
4. Commiter + push
5. Puis dans chaque projet : `stx claude update` pour deployer la nouvelle commande

---

## 2. Taches transverses — Modifier la librairie ET propager

C'est le scenario le plus frequent et le plus important a bien gerer.

### Scenario : "Modifier `st_list` dans la librairie et mettre a jour les manuels"

**Etape 1** — Modifier la librairie :
```bash
cd ~/dev/streamtex-dev/streamtex
claude
# → "Ajoute le parametre align='center' a st_list"
# Claude modifie streamtex/list.py, tests/test_list.py
# /developer:test-run pour valider
```

**Etape 2** — Mettre a jour les manuels (DEPUIS LA MEME SESSION ou une nouvelle) :

**Option A : Rester dans le meme Claude** (recommande si la modif est simple)
```
# Toujours dans le Claude lance depuis streamtex/
→ "Maintenant, mets a jour le bloc bck_lists.py du manual intro
   pour montrer la nouvelle fonctionnalite align.
   Le fichier est dans ../streamtex-docs/manuals/stx_manual_intro/blocks/_atomic/bck_lists.py"
```
Claude PEUT lire et ecrire dans `../streamtex-docs/` meme s'il est lance depuis `streamtex/`.
Il n'aura pas les commandes `/designer:*` mais il connait StreamTeX grace au profil library.

**Option B : Lancer un deuxieme Claude** (recommande si la mise a jour des docs est substantielle)
```bash
# Nouveau terminal
cd ~/dev/streamtex-dev/streamtex-docs
claude
# → "Mets a jour le bloc bck_lists dans le manual intro
#    pour utiliser le nouveau parametre align='center' de st_list"
# Claude a le profil documentation avec toutes les commandes designer
```

**Etape 3** — Verifier que les manuels tournent avec la lib modifiee :
```bash
cd ~/dev/streamtex-dev/streamtex-docs
uv run streamlit run manuals/stx_manual_intro/book.py
# Grace a [tool.uv.sources], streamtex pointe vers ../streamtex (editable)
# → La modif de st_list est IMMEDIATEMENT visible, sans pip install
```

**Etape 4** — Commiter dans chaque repo :
```bash
cd ~/dev/streamtex-dev/streamtex
git add -A && git commit -m "feat(list): add align parameter to st_list"

cd ~/dev/streamtex-dev/streamtex-docs
git add -A && git commit -m "docs: showcase st_list align parameter"
```

### Scenario : "Modifier la librairie et mettre a jour un projet"

Identique au scenario ci-dessus, mais avec le projet :
```bash
# Etape 1 : modifier dans streamtex/
# Etape 2 : mettre a jour dans projects/stx-ai4se/
#   (via le meme Claude ou un deuxieme)
# Etape 3 : tester
cd ~/dev/streamtex-dev/projects/stx-ai4se
uv run streamlit run book.py   # streamtex editable via [tool.uv.sources]
```

---

## 3. Matrice d'acces Claude par emplacement de lancement

| Lance depuis | Profil Claude | Commandes dispo | Peut lire/ecrire | Limitation |
|---|---|---|---|---|
| `streamtex/` | library | test-run, lint, deploy | Librairie + tests + tout le filesystem | Pas de commandes designer |
| `streamtex-docs/` | documentation | designer(7), course-generate, test-run, lint | Manuels + refs + tout le filesystem | Pas de commande deploy PyPI |
| `projects/ai4se/` | presentation | designer(10), migration(5), project(3), dev(2) | Projet + tout le filesystem | Pas de commande deploy PyPI |
| `projects/autre/` | project | designer(7), migration(5), project(3), dev(2) | Projet + tout le filesystem | Pas de commandes presentation |
| `streamtex-claude/` | aucun | aucune specifique | Profils Claude + tout le filesystem | Pas d'identite StreamTeX |

**Important** : "tout le filesystem" signifie que Claude lance dans `streamtex/` PEUT lire
et modifier des fichiers dans `../streamtex-docs/` ou `../projects/stx-ai4se/`.
Ce qui change selon l'emplacement c'est le **profil** (commandes slash, skills, identite CLAUDE.md),
pas l'acces aux fichiers.

---

## 4. Recette par tache concrète

### 4.1 "Je veux creer un nouveau bloc dans un manual"

```bash
cd ~/dev/streamtex-dev/streamtex-docs
claude
# → /designer:block-new bck_mon_nouveau_bloc
```

### 4.2 "Je veux creer un nouveau projet StreamTeX"

```bash
cd ~/dev/streamtex-dev
stx project new mon-cours --profile project
cd projects/stx-mon-cours
claude
# → Le profil 'project' est installe, toutes les commandes disponibles
```

### 4.3 "Je veux publier une nouvelle version de la librairie"

```bash
cd ~/dev/streamtex-dev/streamtex
claude
# → "Bump la version a 0.4.0, mets a jour CHANGELOG.md"
# → /developer:test-run
# → /developer:lint

# Manuellement :
git tag v0.4.0 && git push origin v0.4.0
# → GitHub Actions declenche publish.yml → PyPI
```

### 4.4 "Je veux deployer un projet sur Render"

```bash
cd ~/dev/streamtex-dev/projects/stx-ai4se
stx deploy preflight .
stx deploy render . --name stx-ai4se
```

### 4.5 "Je veux deployer les manuels sur Render"

```bash
cd ~/dev/streamtex-dev/streamtex-docs
stx deploy render . --multi
# → Genere/met a jour render.yaml avec 4 services
# → Guide le deploiement
```

### 4.6 "Je veux deployer un projet sur HuggingFace"

```bash
cd ~/dev/streamtex-dev/projects/stx-ai4se
stx deploy huggingface . https://huggingface.co/spaces/nicolasguelfi/ai4se
```

### 4.7 "Je veux voir l'etat de tout mon workspace"

```bash
cd ~/dev/streamtex-dev
stx workspace status
```

### 4.8 "Je veux ajouter un nouveau skill Claude pour les projets"

```bash
cd ~/dev/streamtex-dev/streamtex-claude
claude
# → Editer profiles/project/designer/skills/mon-skill.md
# → Mettre a jour profiles/project/manifest.toml
# Commiter + push

# Puis propager aux projets :
stx claude update ~/dev/streamtex-dev/projects/stx-ai4se
stx claude update ~/dev/streamtex-dev/streamtex-docs
```

### 4.9 "Je veux lancer tous les manuels en local pour tester"

```bash
cd ~/dev/streamtex-dev/streamtex-docs
uv run streamlit run manuals/stx_manual_intro/book.py &          # port 8501
uv run streamlit run manuals/stx_manual_advanced/book.py --server.port 8502 &
uv run streamlit run manuals/stx_manual_deploy/book.py --server.port 8503 &
uv run streamlit run manuals/stx_manuals_collection/book.py --server.port 8504 &
```

### 4.10 "J'ai modifie la lib, je veux verifier que TOUT fonctionne"

```bash
# 1. Tests unitaires de la librairie
cd ~/dev/streamtex-dev/streamtex
uv run pytest tests/ -v

# 2. Synchro des dependances dans chaque repo
stx workspace sync

# 3. Verification manuelle rapide
cd ~/dev/streamtex-dev/streamtex-docs
uv run streamlit run manuals/stx_manual_intro/book.py

cd ~/dev/streamtex-dev/projects/stx-ai4se
uv run streamlit run book.py
```

---

## 5. Questions frequentes

### "Si je lance Claude dans streamtex/, peut-il modifier les manuels ?"

**Oui.** Claude peut lire et modifier n'importe quel fichier du filesystem. En revanche il
n'aura pas les commandes `/designer:*` (il est en profil `library`). Pour des modifications
simples (mettre a jour un exemple, corriger un import), c'est suffisant. Pour des taches
de design avancees, mieux vaut lancer un Claude dans `streamtex-docs/`.

### "Est-ce que je dois publier sur PyPI a chaque modif de la lib ?"

**Non.** Grace a `[tool.uv.sources]`, les repos `streamtex-docs` et les projets utilisent
la librairie en mode editable. Toute modification de `streamtex/*.py` est instantanement
visible. PyPI n'est necessaire que pour :
- Bob (utilisateur externe)
- Les deploiements Render/HuggingFace (Docker installe depuis PyPI)

### "Comment je sais quel profil Claude est installe dans un projet ?"

```bash
cat ~/dev/streamtex-dev/projects/stx-ai4se/.claude/.stx-profile
# → presentation
```
Ou : `stx claude list` depuis n'importe ou.

### "Est-ce que deux Claude en parallele vont se marcher dessus ?"

Non, tant qu'ils ne modifient pas le meme fichier. Cas d'usage courant :
- Terminal 1 : Claude dans `streamtex/` modifie la lib
- Terminal 2 : Claude dans `streamtex-docs/` cree un nouveau bloc
- Pas de conflit car fichiers differents

Si les deux touchent le meme fichier (rare), Git detectera le conflit au commit.

### "Pourquoi ne pas lancer Claude au niveau du workspace racine ?"

Parce qu'au niveau `~/dev/streamtex-dev/` il n'y a pas de `.claude/` ni de `CLAUDE.md`.
Claude serait generique, sans connaitre StreamTeX. C'est le profil qui donne a Claude
son identite et ses competences. Chaque repo a le profil adapte a sa tache.

### "Et si je veux TOUT dans un seul Claude ?"

C'est le compromis : un seul Claude ne peut charger qu'un seul profil. Pour avoir toutes
les commandes, il faudrait un profil "all" qui combine tout. C'est possible mais deconseille
car les regles de contexte (ex: "48pt minimum" du profil presentation) pollueraient le
travail sur la librairie. Mieux vaut garder les profils separes et utiliser la capacite
de Claude a lire des fichiers cross-repo quand necessaire.

---

## 6. Aide-memoire rapide

| Je veux... | Ou | Commande |
|---|---|---|
| Modifier la librairie | `streamtex/` | `claude` |
| Creer un bloc dans un manual | `streamtex-docs/` | `claude` → `/designer:block-new` |
| Creer un slide de presentation | `projects/ai4se/` | `claude` → `/designer:slide-new` |
| Creer un nouveau projet | workspace root | `stx project new <nom>` |
| Installer un profil Claude | n'importe ou | `stx claude install <profil> <chemin>` |
| Lancer les tests de la lib | `streamtex/` | `uv run pytest tests/ -v` |
| Deployer sur Render | le repo du projet | `stx deploy render .` |
| Deployer sur HuggingFace | le repo du projet | `stx deploy huggingface . <url>` |
| Publier sur PyPI | `streamtex/` | `stx publish pypi` |
| Voir l'etat du workspace | workspace root | `stx workspace status` |
| Mettre a jour les profils Claude | n'importe ou | `stx claude update <chemin>` |
