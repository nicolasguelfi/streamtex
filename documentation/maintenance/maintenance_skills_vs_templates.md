# Plan de Maintenance : Skills Claude vs Script de Generation de Templates

> **Date** : 2026-03-02
> **Auteur** : Nicolas Guelfi + Claude
> **Version** : 1.0
> **Statut** : A FAIRE
> **Remplace** : `maintenance_templates_from_manuals.md` (script de generation — abandonne)

---

## Table des matieres

1. [Decision et justification](#1-decision-et-justification)
2. [Etat des lieux actuel](#2-etat-des-lieux-actuel)
3. [Architecture cible](#3-architecture-cible)
4. [Phase 1 : Consolider les templates statiques](#4-phase-1--consolider-les-templates-statiques)
5. [Phase 2 : Creer la skill `project-init`](#5-phase-2--creer-la-skill-project-init)
6. [Phase 3 : Enrichir `block-new` avec des blueprints](#6-phase-3--enrichir-block-new-avec-des-blueprints)
7. [Phase 4 : Creer la skill `project-customize`](#7-phase-4--creer-la-skill-project-customize)
8. [Phase 5 : Ajouter un agent `project-architect`](#8-phase-5--ajouter-un-agent-project-architect)
9. [Phase 6 : Nettoyage et documentation](#9-phase-6--nettoyage-et-documentation)
10. [Estimation de l'effort](#10-estimation-de-leffort)
11. [Matrice de comparaison](#11-matrice-de-comparaison)
12. [Checklist de validation](#12-checklist-de-validation)

---

## 1. Decision et justification

### 1.1 Decision

**Abandonner** le script `scripts/generate_templates.py` (12-15h de travail prevu) et **investir**
dans des skills Claude specialisees qui generent du code adapte au contexte.

### 1.2 Pourquoi abandonner le script ?

| Probleme | Impact |
|----------|--------|
| Marqueurs FEATURE/DEMO a ajouter dans **tous** les blocks des manuels | Pollution du code source pedagogique |
| Parsing AST ou line-based fragile | Casse a chaque refactoring de block |
| Templates generes = figes | Un template "simple" ne couvre pas les besoins reels |
| Maintenance du script + des marqueurs + de `template_mapping.toml` | Triple cout de maintenance |
| 12-15h de travail pour un resultat peu flexible | Mauvais retour sur investissement |
| Les templates existants (`template_project/`, `template_collection/`) fonctionnent deja | Le probleme est resolu "good enough" |

### 1.3 Pourquoi les skills Claude ?

| Avantage | Detail |
|----------|--------|
| **Adaptatif** | "Cree un projet pour un cours Docker de 8 slides" → code sur mesure |
| **Toujours a jour** | Les skills lisent `coding_standards.md` a chaque invocation |
| **Maintenable** | Modifier une skill = modifier 1 fichier markdown |
| **Incremental** | L'utilisateur peut iterer ("ajoute une slide", "change le style") |
| **Infrastructure existante** | 4 profils, 23+ commandes, 2 agents deja en place |
| **Pas de code a maintenir** | Pas de script Python, pas de parsing, pas de tests specifiques |

### 1.4 Le compromis hybride

```
Templates statiques (stx project new)    → Scaffolding rapide, fonctionne offline
Skills Claude (commandes dans le profil) → Personnalisation, generation contextuelle
```

L'utilisateur sans Claude obtient un projet fonctionnel.
L'utilisateur avec Claude obtient un projet sur mesure.

---

## 2. Etat des lieux actuel

### 2.1 Templates existants (dans streamtex-docs)

| Template | Contenu | Statut |
|----------|---------|--------|
| `templates/template_project/` | 9 blocks, book.py avec TOC/pagination/banner/marker, custom/styles.py complet | Fonctionnel |
| `templates/template_collection/` | book.py avec st_collection, collection.toml, bck_home.py | Fonctionnel |

Ces templates sont maintenus manuellement et sont **suffisants** pour le scaffolding.

### 2.2 CLI `stx project new` (dans streamtex)

| Commande | Ce qu'elle fait | Limitation |
|----------|----------------|------------|
| `stx project new <name>` | Genere book.py, blocks/__init__.py, bck_hello.py, custom/styles.py, .streamlit/config.toml | Scaffolding minimal — un seul block "Hello" |
| `stx project new <name> --collection` | Variante collection avec collection.toml | Idem — minimal |

**Gap identifie** : `stx project new` genere un scaffold minimal, pas les templates riches
de `streamtex-docs/templates/`. Les deux systemes ne sont pas connectes.

### 2.3 Skills/commandes Claude existantes

#### Profil `project` (23 elements — le plus complet)

**Designer** (7 commandes) :
| Commande | Role | Statut |
|----------|------|--------|
| `/designer:block-new` | Creer un nouveau block | Fonctionnel |
| `/designer:slide-new` | Creer un block presentation | Fonctionnel |
| `/designer:slide-audit` | Auditer un block | Fonctionnel |
| `/designer:slide-fix` | Corriger un block | Fonctionnel |
| `/designer:block-preview` | Previsualiser un block | Fonctionnel |
| `/designer:style-audit` | Auditer les styles | Fonctionnel |
| `/designer:style-refactor` | Refactorer les styles | Fonctionnel |

**Migration** (5 commandes) :
| Commande | Role | Statut |
|----------|------|--------|
| `/migration:html-migrate` | Convertir HTML → StreamTeX | Fonctionnel |
| `/migration:html-convert-block` | Convertir un block HTML | Fonctionnel |
| `/migration:html-convert-batch` | Conversion batch | Fonctionnel |
| `/migration:html-export` | Export HTML | Fonctionnel |
| `/migration:conversion-audit` | Audit qualite conversion | Fonctionnel |

**Project** (3 commandes) :
| Commande | Role | Statut |
|----------|------|--------|
| `/project:project-upgrade` | Upgrader un projet vers le dernier template | Fonctionnel |
| `/project:collection-new` | Initialiser une collection | Fonctionnel |
| `/project:course-generate` | Generer book.py depuis blocks.csv | Fonctionnel |

**Developer** (2 commandes) :
| Commande | Role | Statut |
|----------|------|--------|
| `/developer:test-run` | Lancer les tests | Fonctionnel |
| `/developer:lint` | Lancer le linter | Fonctionnel |

**Skills** (3 fichiers) : visual-design-rules.md, style-conventions.md, streamtex-quick-reference.md
**Agents** (2) : slide-designer.md, slide-reviewer.md

#### Ce qui MANQUE

| Element manquant | Description |
|------------------|-------------|
| `/project:project-init` | Initialiser un projet complet interactivement (pas juste le scaffold) |
| Blueprints dans `block-new` | Catalogue de modeles de blocks (comparaison, timeline, galerie...) |
| `/project:project-customize` | Personnaliser un projet existant (styles, theme, navigation) |
| Agent `project-architect` | Concevoir la structure d'un projet complet (combien de blocks, quoi dedans) |

---

## 3. Architecture cible

### 3.1 Flux utilisateur complet (apres implementation)

```
SANS CLAUDE (offline, CI/CD)                  AVEC CLAUDE (interactif)
──────────────────────────                    ────────────────────────

stx project new mon-cours                     stx project new mon-cours
    │                                             │
    ▼                                             ▼
Scaffold minimal :                            Scaffold minimal :
  book.py (1 block)                             book.py (1 block)
  blocks/bck_hello.py                           blocks/bck_hello.py
  custom/styles.py                              custom/styles.py
    │                                             │
    ▼                                             ▼
L'utilisateur code                            claude
a la main                                         │
                                                  ▼
                                         /project:project-init
                                         "cours Docker, 8 slides,
                                          style presentation"
                                              │
                                              ▼
                                         Claude genere :
                                           book.py (8 blocks)
                                           blocks/bck_01_intro.py
                                           blocks/bck_02_containers.py
                                           ... (6 autres)
                                           custom/styles.py (adapte)
                                              │
                                              ▼
                                         /designer:block-new
                                         "slide comparaison VM vs
                                          Containers, grille 2 cols"
                                              │
                                              ▼
                                         Claude genere :
                                           bck_09_vm_vs_containers.py
                                           (sur mesure)
```

### 3.2 Organisation des skills dans le profil `project`

```
profiles/project/
├── commands/
│   ├── designer/
│   │   ├── block-new.md          ← ENRICHIR (ajouter blueprints)
│   │   ├── slide-new.md          (existant, inchange)
│   │   ├── slide-audit.md        (existant, inchange)
│   │   ├── slide-fix.md          (existant, inchange)
│   │   ├── block-preview.md      (existant, inchange)
│   │   ├── style-audit.md        (existant, inchange)
│   │   └── style-refactor.md     (existant, inchange)
│   ├── project/
│   │   ├── project-init.md       ← NOUVEAU — initialisation interactive
│   │   ├── project-customize.md  ← NOUVEAU — personnalisation du projet
│   │   ├── project-upgrade.md    (existant, inchange)
│   │   ├── collection-new.md     (existant, inchange)
│   │   └── course-generate.md    (existant, inchange)
│   ├── migration/                (existant, inchange)
│   └── developer/                (existant, inchange)
│
├── designer/
│   ├── agents/
│   │   ├── slide-designer.md     (existant, inchange)
│   │   ├── slide-reviewer.md     (existant, inchange)
│   │   └── project-architect.md  ← NOUVEAU — agent de conception de projet
│   └── skills/
│       ├── visual-design-rules.md       (existant, inchange)
│       ├── style-conventions.md         (existant, inchange)
│       ├── streamtex-quick-reference.md (existant, inchange)
│       └── block-blueprints.md          ← NOUVEAU — catalogue de modeles
│
└── references/                   (existant, inchange)
    ├── coding_standards.md
    └── streamtex_cheatsheet_en.md
```

**Resume des changements : 2 nouvelles commandes, 1 nouvel agent, 1 nouvelle skill, 1 commande enrichie**

---

## 4. Phase 1 : Consolider les templates statiques

> **Effort** : 1-2h
> **Objectif** : Connecter `stx project new` aux templates riches existants

### 4.1 Probleme actuel

`stx project new` genere un scaffold minimal (1 block "Hello"), alors que
`streamtex-docs/templates/template_project/` contient un projet complet (9 blocks).
Les deux ne sont pas connectes.

### 4.2 Solution

Ajouter une option `--template` a `stx project new` :

```bash
# Scaffold minimal (comportement actuel, inchange)
stx project new mon-cours

# Projet complet depuis le template riche
stx project new mon-cours --template project

# Collection depuis le template riche
stx project new mon-cours --template collection
```

### 4.3 Implementation

Modifier `project_cmd.py` :

```python
@click.option("--template", default=None, type=click.Choice(["project", "collection"]),
              help="Use a rich template from streamtex-docs.")
def new(name, profile, is_collection, no_git, no_sync, no_claude, template):
    if template:
        # Copier le template depuis streamtex-docs/templates/template_<template>/
        ws_root = find_workspace_root()
        if ws_root:
            src = os.path.join(ws_root, "streamtex-docs", "templates", f"template_{template}")
            if os.path.isdir(src):
                shutil.copytree(src, target, dirs_exist_ok=True)
                # Remplacer les noms dans les fichiers generes
                ...
    else:
        # Scaffold minimal (comportement actuel)
        scaffold_project(target, name, collection=is_collection)
```

### 4.4 Tests a ajouter

```python
def test_new_with_template_project(tmp_path):
    """stx project new --template project copie le template riche."""
    ...

def test_new_with_template_collection(tmp_path):
    """stx project new --template collection copie le template collection."""
    ...

def test_new_template_requires_workspace(tmp_path):
    """--template echoue si pas dans un workspace avec streamtex-docs."""
    ...
```

### 4.5 Fichiers a modifier

| Fichier | Modification |
|---------|-------------|
| `streamtex/cli/project_cmd.py` | Ajouter option `--template`, logique de copie |
| `tests/test_cli_project.py` | 3 nouveaux tests |

---

## 5. Phase 2 : Creer la skill `project-init`

> **Effort** : 2-3h
> **Objectif** : Permettre a Claude de generer un projet complet et adapte au contexte

### 5.1 Ce que fait `/project:project-init`

L'utilisateur decrit son projet en langage naturel, Claude genere tous les fichiers.

**Exemples d'invocation** :

```
/project:project-init "cours Docker pour debutants, 8 slides, style presentation sombre"

/project:project-init "documentation technique API REST, 12 sections, avec exemples de code"

/project:project-init "portfolio de projets recherche, 5 projets, mode collection"
```

### 5.2 Specification de la commande

**Fichier** : `profiles/project/commands/project/project-init.md`

```markdown
# /project:project-init — Initialiser un projet StreamTeX complet

## Declencheur
L'utilisateur decrit un projet en langage naturel.

## Lectures obligatoires AVANT generation
1. `.claude/references/coding_standards.md`
2. `.claude/references/streamtex_cheatsheet_en.md`
3. `.claude/designer/skills/visual-design-rules.md`
4. `.claude/designer/skills/style-conventions.md`
5. `book.py` existant (si le projet a deja ete scaffold)

## Workflow

### Etape 1 : Analyser la demande
Extraire de la description :
- **Type** : presentation | documentation | collection
- **Nombre de sections/slides** : N
- **Theme visuel** : sombre | clair | custom
- **Fonctionnalites** : TOC, pagination, banner, export, interactivite
- **Public cible** : amphitheatre (gros texte) | ecran (texte normal)

### Etape 2 : Proposer un plan
Afficher a l'utilisateur :
- Liste des N blocks avec noms et descriptions
- Structure du book.py (pagination, TOC, banner)
- Palette de couleurs proposee
- Fonctionnalites activees

Demander confirmation avant de generer.

### Etape 3 : Generer les fichiers
Pour chaque block :
1. Creer `blocks/bck_NN_<nom>.py` avec :
   - Docstring descriptive
   - `BlockStyles` adapte au theme
   - `def build()` avec contenu placeholder structure
   - Imports conformes aux coding_standards.md
2. Mettre a jour `book.py` avec la liste des blocks
3. Adapter `custom/styles.py` avec la palette choisie
4. Adapter `custom/themes.py` si necessaire

### Etape 4 : Valider
- Verifier que tous les blocks sont importables
- Verifier la coherence du book.py
- Afficher un resume des fichiers generes

## Regles de generation
- Tous les blocks suivent le pattern BlockStyles + build()
- Les noms de styles sont en anglais (style-conventions.md)
- Les tailles de texte respectent le public cible :
  - Amphitheatre : s.Large minimum pour le corps
  - Ecran : s.large pour le corps
- Chaque block a un `toc_lvl` pour le sommaire
- Le contenu est du placeholder structure (pas du Lorem Ipsum) :
  - Titres descriptifs du sujet reel
  - Bullet points avec "[A completer : ...]"
  - Emplacements d'images avec commentaires
```

### 5.3 Exemple de sortie

Pour `/project:project-init "cours Docker, 6 slides, presentation amphi"` :

```
Je propose la structure suivante :

 1. bck_01_titre         — Slide de titre du cours
 2. bck_02_intro_docker  — Qu'est-ce que Docker ? (3 bullets)
 3. bck_03_architecture  — Architecture Docker (schema)
 4. bck_04_images_containers — Images vs Containers (grille 2 cols)
 5. bck_05_demo_live     — Demo : premier container (code + terminal)
 6. bck_06_conclusion    — Points cles + prochaines etapes

Configuration :
- Pagination : activee (1 slide par page)
- TOC : sidebar avec numerotation
- Banner : titre du cours en haut
- Theme : sombre, palette accent bleu

Voulez-vous que je genere ces fichiers ?
```

---

## 6. Phase 3 : Enrichir `block-new` avec des blueprints

> **Effort** : 2h
> **Objectif** : Offrir un catalogue de modeles de blocks courants

### 6.1 Probleme actuel

`/designer:block-new` cree un block vide standard. L'utilisateur doit ensuite decrire
en detail ce qu'il veut. Pas de modeles pre-definis pour les patterns courants.

### 6.2 Solution : Skill `block-blueprints.md`

**Fichier** : `profiles/project/designer/skills/block-blueprints.md`

Ce fichier documente des modeles de blocks courants que Claude peut utiliser comme reference
quand il genere du code via `/designer:block-new`.

### 6.3 Catalogue des blueprints

```markdown
# Block Blueprints — Catalogue de modeles

## Comment utiliser
Quand l'utilisateur demande un type de block connu, utiliser le blueprint
correspondant comme base et l'adapter au contexte.

---

## Blueprint 1 : Titre (bck_title)
Un slide de titre avec nom du cours/projet, sous-titre, auteur.

Structure :
- st_space (grand)
- st_write Huge : titre
- st_write Large : sous-titre
- st_space
- st_write large + muted : auteur / date

## Blueprint 2 : Section Header (bck_section)
Slide d'introduction de section avec numero et titre.

Structure :
- st_block (centre)
  - st_write huge : "Section N"
  - st_write LARGE : titre de la section
  - st_space
  - st_write large : description courte (1-2 lignes)

## Blueprint 3 : Contenu textuel (bck_content)
Slide avec titre + bullets.

Structure :
- st_write huge : titre (toc_lvl="2")
- st_space
- st_list ul : 3-5 bullets (Large pour amphi, large pour ecran)

## Blueprint 4 : Comparaison 2 colonnes (bck_comparison)
Slide avec 2 colonnes comparant des concepts.

Structure :
- st_write huge : titre
- st_space
- st_grid [1, 1] :
  - Colonne gauche : titre + bullets concept A
  - Colonne droite : titre + bullets concept B

## Blueprint 5 : Image + Texte (bck_image_text)
Slide avec image a gauche et texte explicatif a droite.

Structure :
- st_write huge : titre
- st_space
- st_grid [1, 1] :
  - st_image : illustration
  - st_write : description + bullets

## Blueprint 6 : Code + Resultat (bck_code_demo)
Slide montrant du code et son resultat.

Structure :
- st_write huge : titre
- st_space
- st_grid [1, 1] :
  - st_code : code source
  - st_block : resultat / output

## Blueprint 7 : Timeline / Etapes (bck_timeline)
Slide avec une sequence d'etapes numerotees.

Structure :
- st_write huge : titre
- st_space
- Pour chaque etape :
  - st_grid [auto, 1fr] :
    - st_write LARGE + accent : "N."
    - st_write Large : description de l'etape

## Blueprint 8 : Citation / Highlight (bck_quote)
Slide avec une citation ou un message cle mis en avant.

Structure :
- st_space (grand)
- st_block (fond accent, padding)
  - st_write Huge + italic : citation
  - st_space
  - st_write Large + muted : attribution

## Blueprint 9 : Galerie d'images (bck_gallery)
Slide avec une grille d'images.

Structure :
- st_write huge : titre
- st_space
- st_grid [1, 1, 1] :
  - st_image + legende (x3 ou x6)

## Blueprint 10 : Conclusion / Points cles (bck_conclusion)
Slide de synthese avec les points importants.

Structure :
- st_write huge : "Points cles" ou "A retenir"
- st_space
- st_list ul avec icone check :
  - 3-5 points essentiels (Large)
- st_space
- st_write large + muted : "Prochaines etapes..."
```

### 6.4 Mise a jour de `block-new.md`

Ajouter dans la commande existante :

```markdown
## Etape 2b : Verifier les blueprints
Avant de generer, consulter `.claude/designer/skills/block-blueprints.md`
pour verifier si un blueprint correspond au besoin.
Si oui, l'utiliser comme base et l'adapter.

Exemples de correspondance :
- "slide de titre" → Blueprint 1 (bck_title)
- "comparaison X vs Y" → Blueprint 4 (bck_comparison)
- "demo de code" → Blueprint 6 (bck_code_demo)
- "resume" ou "conclusion" → Blueprint 10 (bck_conclusion)
```

### 6.5 Fichiers a creer/modifier

| Fichier | Action |
|---------|--------|
| `profiles/project/designer/skills/block-blueprints.md` | CREER — catalogue des 10 blueprints |
| `profiles/project/commands/designer/block-new.md` | MODIFIER — ajouter etape 2b (consultation blueprints) |

---

## 7. Phase 4 : Creer la skill `project-customize`

> **Effort** : 1-2h
> **Objectif** : Permettre de personnaliser un projet existant en une commande

### 7.1 Ce que fait `/project:project-customize`

Personnaliser les aspects visuels et structurels d'un projet existant.

**Exemples** :

```
/project:project-customize "passer en theme clair avec palette verte"

/project:project-customize "ajouter un TOC sidebar avec numerotation"

/project:project-customize "activer l'export HTML et le mode banner"

/project:project-customize "adapter pour projection en amphitheatre (gros texte)"
```

### 7.2 Specification

**Fichier** : `profiles/project/commands/project/project-customize.md`

```markdown
# /project:project-customize — Personnaliser un projet StreamTeX

## Declencheur
L'utilisateur decrit les changements souhaites en langage naturel.

## Lectures obligatoires
1. `book.py` — configuration actuelle
2. `custom/styles.py` — palette actuelle
3. `custom/themes.py` — theme actuel
4. `.claude/references/coding_standards.md`
5. `.claude/designer/skills/style-conventions.md`

## Domaines de personnalisation

### Theme et couleurs
- Palette de couleurs (primary, accent, highlight, success, muted)
- Theme Streamlit (dark/light)
- Couleurs de fond des blocks

### Typographie
- Tailles de police (ecran vs amphitheatre)
- Hierarchie des titres
- Style des bullets

### Navigation
- TOC : on/off, mode de numerotation, position sidebar
- Pagination : on/off
- Marker : on/off, touches de navigation
- Banner : on/off, configuration

### Fonctionnalites
- Export HTML : on/off
- Inspector : on/off
- Zoom : on/off, valeur par defaut
- Mode collection : on/off

## Workflow
1. Lire la configuration actuelle
2. Identifier les changements demandes
3. Proposer les modifications (diff)
4. Appliquer apres confirmation
```

---

## 8. Phase 5 : Ajouter un agent `project-architect`

> **Effort** : 1h
> **Objectif** : Un role d'agent pour concevoir la structure d'un projet avant la generation

### 8.1 Ce que fait l'agent

L'agent `project-architect` est un role specialise que Claude adopte quand il planifie
la structure d'un projet. Il est consulte implicitement par `/project:project-init`.

### 8.2 Specification

**Fichier** : `profiles/project/designer/agents/project-architect.md`

```markdown
# Agent : Project Architect

## Role
Tu concois la structure de projets StreamTeX. Tu determines le nombre de blocks,
leur contenu, leur ordre, et les fonctionnalites necessaires.

## Lectures obligatoires
1. coding_standards.md
2. streamtex_cheatsheet_en.md
3. block-blueprints.md
4. visual-design-rules.md

## Principes de conception

### Structure
- Un block = une idee / un sujet
- Ordre logique : introduction → developpement → conclusion
- Pas plus de 15 blocks par projet (au-dela, envisager une collection)
- Nommer les blocks : bck_NN_description_courte.py

### Progression pedagogique
Pour les cours/formations :
1. Contexte et objectifs
2. Concepts fondamentaux (du simple au complexe)
3. Demonstrations pratiques
4. Exercices ou points cles
5. Synthese et prochaines etapes

### Fonctionnalites
Choisir selon le type de projet :

| Type | Pagination | TOC | Banner | Marker | Export |
|------|-----------|-----|--------|--------|--------|
| Presentation amphi | oui | sidebar | oui | oui (PageUp/Down) | non |
| Documentation | non (scroll) | sidebar numerote | non | non | oui (HTML) |
| Collection | non | non | non | non | non |

### Anti-patterns
- Trop de blocks (>15) → decouper en collection
- Blocks trop longs (>200 lignes) → decouper en atomics
- Pas de fil conducteur → ajouter des blocks de transition
- Tout dans un seul block → decouper par concept
```

---

## 9. Phase 6 : Nettoyage et documentation

> **Effort** : 1h
> **Objectif** : Marquer le plan precedent comme abandonne, documenter les nouvelles skills

### 9.1 Fichiers a modifier

| Fichier | Action |
|---------|--------|
| `maintenance_templates_from_manuals.md` | Ajouter un bandeau "ABANDONNE — remplace par maintenance_skills_vs_templates.md" |
| `streamtex-claude/README.md` | Documenter les nouvelles commandes |

### 9.2 Mettre a jour le guide stx-guide

Ajouter les nouvelles commandes dans la section des skills Claude disponibles.

### 9.3 Tester les skills

Tester chaque nouvelle skill manuellement :

```bash
# Test 1 : project-init
cd stx-html-example
claude
> /project:project-init "site vitrine avec 4 sections : accueil, produits, equipe, contact"

# Test 2 : block-new avec blueprint
> /designer:block-new "slide comparaison React vs Vue, grille 2 colonnes"

# Test 3 : project-customize
> /project:project-customize "passer en theme clair, palette bleue et orange"
```

---

## 10. Estimation de l'effort

### Plan abandonne (script de generation)

| Phase | Effort | Valeur |
|-------|--------|--------|
| P1 : Marqueurs FEATURE/DEMO | 2-3h | Faible (pollue le code) |
| P2 : Script generate_templates.py | 6-8h | Moyenne (templates figes) |
| P3 : Integration CLI | 1h | Faible |
| P4 : Nettoyage | 30min | - |
| P5 : Validation | 2h | - |
| **Total** | **12-15h** | **Moyenne** |

### Nouveau plan (skills Claude)

| Phase | Effort | Valeur |
|-------|--------|--------|
| P1 : Consolider templates + option `--template` | 1-2h | Haute (connecte les templates existants) |
| P2 : Skill `project-init` | 2-3h | Tres haute (generation contextuelle) |
| P3 : Blueprints dans `block-new` | 2h | Haute (catalogue reutilisable) |
| P4 : Skill `project-customize` | 1-2h | Haute (personnalisation en 1 commande) |
| P5 : Agent `project-architect` | 1h | Moyenne (role de conception) |
| P6 : Nettoyage + documentation | 1h | - |
| **Total** | **8-11h** | **Tres haute** |

### Comparaison

| Critere | Script (abandonne) | Skills (nouveau) |
|---------|-------------------|-----------------|
| Effort total | 12-15h | 8-11h |
| Maintenance long terme | Elevee | Faible |
| Flexibilite | Faible (templates figes) | Tres haute |
| Fonctionne sans Claude | Oui | Hybrid (scaffold + Claude) |
| Valeur utilisateur | Moyenne | Tres haute |
| Risque technique | Moyen (parsing fragile) | Faible (markdown seulement) |

---

## 11. Matrice de comparaison detaillee

### Scenario : "Je veux creer un projet pour un cours de 10 slides sur Docker"

| Etape | Avec script (abandonne) | Avec skills (nouveau) |
|-------|------------------------|----------------------|
| 1. Scaffolding | `stx project new docker-cours` → template_project copie | `stx project new docker-cours` → scaffold minimal |
| 2. Adaptation | Modifier manuellement les 9 blocks du template, renommer, recrire le contenu | `/project:project-init "cours Docker, 10 slides, presentation amphi"` → Claude genere 10 blocks adaptes |
| 3. Ajout block | Copier un block existant, le modifier | `/designer:block-new "slide comparaison VM vs Containers"` → Claude genere un block sur mesure (utilise blueprint 4) |
| 4. Personnalisation | Modifier styles.py manuellement | `/project:project-customize "palette bleue, gros texte pour amphi"` → Claude adapte styles.py et les blocks |
| 5. Temps total | ~2-4h de travail manuel | ~15-30min d'interaction avec Claude |

### Scenario : "Je veux un portfolio de projets de recherche"

| Etape | Avec script | Avec skills |
|-------|-------------|-------------|
| 1. Scaffolding | `stx project new portfolio --collection` → template_collection copie | `stx project new portfolio --collection` |
| 2. Adaptation | Modifier collection.toml, bck_home.py | `/project:project-init "collection de 5 projets recherche avec cartes et descriptions"` → Claude genere la collection complete |

---

## 12. Checklist de validation

### Phase 1 : Templates statiques

- [ ] Option `--template` ajoutee a `stx project new`
- [ ] `--template project` copie depuis `streamtex-docs/templates/template_project/`
- [ ] `--template collection` copie depuis `streamtex-docs/templates/template_collection/`
- [ ] 3 tests unitaires ajoutees
- [ ] Documentation mise a jour

### Phase 2 : Skill `project-init`

- [ ] Fichier `profiles/project/commands/project/project-init.md` cree
- [ ] Workflow 4 etapes documente
- [ ] Regles de generation conformes aux coding_standards.md
- [ ] Teste manuellement avec 3 scenarios differents

### Phase 3 : Blueprints

- [ ] Fichier `profiles/project/designer/skills/block-blueprints.md` cree
- [ ] 10 blueprints documentes
- [ ] `block-new.md` modifie (etape 2b ajoutee)
- [ ] Teste avec `/designer:block-new` + description correspondant a un blueprint

### Phase 4 : Skill `project-customize`

- [ ] Fichier `profiles/project/commands/project/project-customize.md` cree
- [ ] 4 domaines de personnalisation documentes
- [ ] Teste avec changement de theme, de navigation, de typographie

### Phase 5 : Agent `project-architect`

- [ ] Fichier `profiles/project/designer/agents/project-architect.md` cree
- [ ] Principes de conception documentes
- [ ] Reference par `project-init.md`

### Phase 6 : Nettoyage

- [ ] `maintenance_templates_from_manuals.md` marque comme ABANDONNE
- [ ] `streamtex-claude/README.md` mis a jour
- [ ] Guide stx-guide mis a jour

---

## Annexe A : Ordre d'implementation recommande

```
Semaine 1 :
  Phase 1 (templates statiques)     → 1-2h
  Phase 3 (blueprints)              → 2h

Semaine 2 :
  Phase 2 (project-init)            → 2-3h
  Phase 5 (agent project-architect) → 1h

Semaine 3 :
  Phase 4 (project-customize)       → 1-2h
  Phase 6 (nettoyage)               → 1h
```

La Phase 1 et la Phase 3 sont independantes et peuvent etre faites en parallele.
La Phase 2 depend de la Phase 3 (block-blueprints) et de la Phase 5 (agent).

## Annexe B : Impact sur les profils

| Profil | Impact |
|--------|--------|
| **project** | +2 commandes, +1 agent, +1 skill, 1 commande enrichie |
| **presentation** | Herite automatiquement via l'overlay |
| **documentation** | Herite des commandes project partagees |
| **library** | Aucun impact |
