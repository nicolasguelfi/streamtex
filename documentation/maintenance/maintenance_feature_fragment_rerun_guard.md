# Plan de Maintenance : Fragment Rerun Guard — Mode Continu avec `st.fragment`

> **Date** : 2026-02-27
> **Auteur** : Claude Code (assisté par Nicolas Guelfi)
> **Version** : 2.0
> **Statut** : Plan revise apres analyse des effets de bord
> **Pré-requis** : Streamlit >= 1.37.0 (installé : 1.54.0)

---

## Table des matieres

1. [Probleme et objectif](#1-probleme-et-objectif)
2. [Diagnostic technique](#2-diagnostic-technique)
3. [Strategie de solution](#3-strategie-de-solution)
4. [Plan d'implementation detaille](#4-plan-dimplementation-detaille)
5. [Fichiers impactes](#5-fichiers-impactes)
6. [Tests](#6-tests)
7. [Risques et mitigations](#7-risques-et-mitigations)
8. [Effets de bord visuels pour l'utilisateur final](#8-effets-de-bord-visuels-pour-lutilisateur-final)
9. [Contraintes pour les futurs concepteurs de blocs](#9-contraintes-pour-les-futurs-concepteurs-de-blocs)
10. [Limitations connues](#10-limitations-connues)
11. [Criteres de validation](#11-criteres-de-validation)

---

## 1. Probleme et objectif

### Probleme

En mode continu (`paginate=False`), **tous les blocs** sont rendus sequentiellement a chaque rerun Streamlit. Quand un utilisateur interagit avec un widget dans un seul bloc (ex: clic sur un expander, toggle, slider), **tous les N blocs** sont re-executes. Pour un projet avec 15+ blocs, cela cause :

- Temps de rerun de plusieurs secondes apres chaque interaction
- Risque de crash navigateur pour les tres gros projets (DOM massif recree)
- Experience utilisateur degradee (freeze visible)

### Objectif

Envelopper chaque bloc dans un `st.fragment` pour que les interactions widget ne re-executent que le bloc concerne (O(1) au lieu de O(N) par rerun).

### Perimetre

- **Mode continu uniquement** — le mode pagine est deja O(1) par rerun
- **Zero changement dans le code des blocs existants** — la solution est 100% dans la librairie
- **Preservation complete** de la TOC, des markers, de la recherche et de l'export HTML

---

## 2. Diagnostic technique

### 2.1 Architecture actuelle du rendu continu

```
st_book()
  ├── reset_toc_registry()           # RAZ registre TOC global
  ├── reset_marker_registry()        # RAZ registre markers global
  ├── reset_export_buffer()          # RAZ buffer export global
  ├── start_collector()              # Demarre collecteur recherche
  │
  ├── for i, module in enumerate(module_list):    # BOUCLE PRINCIPALE
  │     ├── collector.set_block(i)                # Indexe le bloc courant
  │     ├── toc_before = len(toc_entries())       # Snapshot TOC
  │     ├── st_include(module)                    # → module.build()
  │     ├── tag new TOC entries with block_idx    # Attribution post-rendu
  │     ├── separator (optionnel)
  │     └── st_space("v", "70px")
  │
  ├── stop_collector()               # Finalise index recherche
  ├── populate_toc()                 # Remplit sidebar TOC
  ├── populate_markers_sidebar()     # Remplit sidebar markers
  ├── inject_marker_navigation()     # Injecte JS navigation
  └── generate_export_html()         # Genere HTML export
```

### 2.2 Probleme racine : les singletons globaux mutables

Quatre registres globaux sont mutes pendant `build()` de chaque bloc :

| Registre | Variable globale | Fonction de mutation | Fichier |
|----------|-----------------|---------------------|---------|
| TOC | `toc` (l.110) | `register_toc_entry()` (l.122) | `toc.py` |
| Markers | `_registry` (l.73) | `register_marker()` (l.87) | `marker.py` |
| Export | `_buffer` (l.124) | `_buffer.append()` via `st_html()` (l.224) | `export.py` |
| Search | `_collector` (l.37) | `record_if_active()` (l.55) | `search.py` |

Lors d'un **fragment rerun** (un seul bloc re-execute), ces registres ne sont PAS reinitialises. Les fonctions de mutation **ajoutent des doublons** aux donnees existantes.

### 2.3 Comment detecter un fragment rerun

Streamlit expose le contexte d'execution via une API interne :

```python
from streamlit.runtime.scriptrunner_utils.script_run_context import get_script_run_ctx

ctx = get_script_run_ctx()
# ctx.fragment_ids_this_run : None ou [] en full rerun, non-vide en fragment rerun
# ctx.current_fragment_id  : None hors fragment, string MD5 dans un fragment
```

### 2.4 Precedent dans le projet : `inspector.py`

Le module `inspector.py` utilise deja `@st.fragment` sur deux fonctions (l.807 et l.831) avec le pattern `st.rerun(scope="app")` pour echapper d'un fragment vers un full rerun quand necessaire.

---

## 3. Strategie de solution

### Principe : Guard global avec flag de contexte

```
Full rerun :
  → reset_*_registry() reinitialise les registres
  → Tous les blocs executent build() et enregistrent TOC/markers/export/search
  → Phase post-rendu construit sidebar et export
  → Comportement identique a aujourd'hui

Fragment rerun (un seul bloc) :
  → Le guard detecte le fragment rerun
  → register_toc_entry() → NO-OP (retourne ancre existante)
  → register_marker() → NO-OP (retourne index existant)
  → _buffer.append() → NO-OP (pas d'ajout au buffer)
  → record_if_active() → NO-OP (pas d'ajout a l'index)
  → Le bloc se rend visuellement normalement (st.html/components.html fonctionnent)
  → TOC/markers/search/export restent inchanges (donnees du dernier full rerun)
```

### Pourquoi cette approche

- **Simple** : un seul mecanisme (detection de contexte) resout les 9 problemes bloquants
- **Non-invasif** : les fonctions de mutation existantes ajoutent juste un `if` en tete
- **Zero impact sur les blocs** : le code des blocs ne change pas
- **Reversible** : si le guard pose probleme, on le desactive et tout redevient comme avant

---

## 4. Plan d'implementation detaille

### Sprint 1 : Module guard central (1 fichier nouveau)

#### Etape 1.1 : Creer `streamtex/fragment_guard.py`

```python
"""Fragment rerun guard for continuous mode.

Prevents global registry mutations (TOC, markers, export, search)
during st.fragment partial reruns. Only the visual rendering
(st.html, components.html) is allowed — registry writes are skipped.
"""

from __future__ import annotations


def is_fragment_rerun() -> bool:
    """Return True if the current execution is a fragment rerun.

    Uses Streamlit's internal ScriptRunContext to detect whether
    the current run was triggered by a widget inside a fragment
    (partial rerun) versus a full app rerun.

    Returns False when:
    - Running in a full app rerun (all blocks re-execute)
    - Running outside Streamlit (e.g., unit tests, imports)
    - The context is unavailable for any reason
    """
    try:
        from streamlit.runtime.scriptrunner_utils.script_run_context import (
            get_script_run_ctx,
        )
    except ImportError:
        return False

    ctx = get_script_run_ctx()
    if ctx is None:
        return False
    return bool(ctx.fragment_ids_this_run)
```

**Justifications** :
- Import lazy de Streamlit (`try/except`) pour ne pas casser les tests unitaires qui n'ont pas de contexte Streamlit
- Fonction pure, sans etat, sans effet de bord
- Un seul point de verite pour toute la librairie

---

### Sprint 2 : Integration du guard dans les 4 registres (4 fichiers modifies)

#### Etape 2.1 : `streamtex/toc.py` — Guard sur `register_toc_entry()`

**Lignes impactees** : 55-99 (`register_entry`), 122-131 (`register_toc_entry`)

> **CORRECTIF v2.0** : Le type de retour est un **3-tuple** `(key_anchor, section_number, lvl)`,
> PAS un simple `str`. Le plan v1.0 contenait un bug qui aurait provoque un crash
> `ValueError: not enough values to unpack` au premier fragment rerun d'un bloc avec `toc_lvl`.

**Prerequis** : Stocker `_section_number` dans chaque entree TOC pour pouvoir le reconstruire
lors du fragment rerun. Modifier `register_entry()` (l.88-94) pour ajouter un champ :

**Modification de `register_entry()`** (ajout d'un champ dans le dict, l.88-94) :
```python
self.get_entries().append({
    "level": lvl,
    "title": section_number + label if has_num else label,
    "key_anchor": key_anchor,
    "_reg_label": label,
    "_reg_level": level,
    "_section_number": section_number if self.config.numerate_titles else "",
})
```

**Avant** (`register_toc_entry`, l.122-131) :
```python
def register_toc_entry(label: str, level: str) -> str:
    global toc
    assert isinstance(toc, TOCRegistry), "..."
    return toc.register_entry(label, level)
```

**Apres** :
```python
def register_toc_entry(label: str, level: str) -> tuple[str, str, int]:
    global toc
    assert isinstance(toc, TOCRegistry), "..."
    from .fragment_guard import is_fragment_rerun
    if is_fragment_rerun():
        # Fragment rerun: return existing entry data without re-registering.
        # The TOC was fully built during the last full rerun.
        return _find_existing_toc_entry(label)
    return toc.register_entry(label, level)
```

**Fonction helper a ajouter** dans `toc.py` :
```python
def _find_existing_toc_entry(label: str) -> tuple[str, str, int]:
    """Find the full (key_anchor, section_number, level) for an existing TOC entry.

    During a fragment rerun, the TOC entries from the full rerun are
    still in the registry. We look up the matching entry and return
    the same 3-tuple that register_entry() would have returned,
    so that write.py line 115 can unpack it correctly:
        key_anchor, section_number, resolved_lvl = register_toc_entry(...)

    Falls back to generating a slug from the label if not found
    (defensive, should not happen in normal operation).
    """
    global toc
    if toc is not None:
        for entry in toc.get_entries():
            if entry.get("_reg_label") == label:
                return (
                    entry.get("key_anchor", ""),
                    entry.get("_section_number", ""),
                    entry.get("level", 1),
                )
    # Fallback: generate anchor from label (same logic as TOCRegistry)
    return TOCRegistry.get_key_anchor(label), "", 1
```

**Raison** : `write.py:115` decompose le retour en 3 variables :
```python
key_anchor, section_number, resolved_lvl = register_toc_entry(label, toc_lvl)
```
Le guard DOIT retourner le meme 3-tuple pour que le HTML genere (ancre, numerotation, niveau)
soit identique a celui du full rerun.

#### Etape 2.2 : `streamtex/marker.py` — Guard sur `register_marker()`

**Lignes impactees** : 87-93

**Avant** :
```python
def register_marker(label: str, anchor: str) -> int:
    global _registry
    assert isinstance(_registry, MarkerRegistry), "..."
    return _registry.register(label, anchor)
```

**Apres** :
```python
def register_marker(label: str, anchor: str) -> int:
    global _registry
    assert isinstance(_registry, MarkerRegistry), "..."
    from .fragment_guard import is_fragment_rerun
    if is_fragment_rerun():
        # Fragment rerun: return existing index without re-registering.
        return _find_existing_marker_index(anchor)
    return _registry.register(label, anchor)
```

**Fonction helper a ajouter** dans `marker.py` :
```python
def _find_existing_marker_index(anchor: str) -> int:
    """Find the index of an already-registered marker by anchor."""
    global _registry
    if _registry is not None:
        for entry in _registry.get_entries():
            if entry.get("anchor") == anchor:
                return entry.get("index", 0)
    return 0
```

**Raison** : `st_marker()` utilise l'index retourne pour generer le HTML du marqueur invisible. L'index doit etre identique au full rerun.

#### Etape 2.3 : `streamtex/export.py` — Guard sur `st_html()` (buffer append)

**Lignes impactees** : 193-230 (fonction `st_html`)

**Avant** (extrait pertinent) :
```python
def st_html(html: str, *, height: int = 0, ...):
    # ... rendu Streamlit (st.html ou components.html) ...
    if _buffer is not None:
        _buffer.append(html)
    from .search import record_if_active
    record_if_active(html)
```

**Apres** :
```python
def st_html(html: str, *, height: int = 0, ...):
    # ... rendu Streamlit (st.html ou components.html) — INCHANGE ...
    from .fragment_guard import is_fragment_rerun
    if not is_fragment_rerun():
        if _buffer is not None:
            _buffer.append(html)
        from .search import record_if_active
        record_if_active(html)
```

**Raison** : Le rendu visuel (`st.html()` / `components.html()`) DOIT s'executer (c'est le but du fragment rerun : mettre a jour l'affichage du bloc). Seuls les effets de bord sur les registres globaux (buffer export + collecteur search) sont inhibes.

**Note** : Les fonctions `export_append()`, `export_push_wrapper()`, `export_pop_wrapper()` (l.145-160) sont aussi appelees directement par `st_block`, `st_grid`, `st_list`. Il faut egalement les guarder :

```python
def export_append(html: str) -> None:
    if _buffer is not None:
        from .fragment_guard import is_fragment_rerun
        if not is_fragment_rerun():
            _buffer.append(html)

def export_push_wrapper(open_tag: str) -> None:
    if _buffer is not None:
        from .fragment_guard import is_fragment_rerun
        if not is_fragment_rerun():
            _buffer.push_wrapper(open_tag)

def export_pop_wrapper(close_tag: str) -> None:
    if _buffer is not None:
        from .fragment_guard import is_fragment_rerun
        if not is_fragment_rerun():
            _buffer.pop_wrapper(close_tag)
```

#### Etape 2.4 : `streamtex/search.py` — Guard sur `record_if_active()`

**Lignes impactees** : 55-57

**Avant** :
```python
def record_if_active(html: str) -> None:
    if _collector is not None:
        _collector.record(html)
```

**Apres** :
```python
def record_if_active(html: str) -> None:
    if _collector is not None:
        from .fragment_guard import is_fragment_rerun
        if not is_fragment_rerun():
            _collector.record(html)
```

**Raison** : L'index de recherche doit rester stable. Le texte du bloc est deja indexe lors du full rerun.

> **Note v2.0 (defense en profondeur)** : Ce guard est techniquement **redondant** car
> `stop_collector()` est appele a `book.py:218` apres la boucle de blocs, ce qui met
> `_collector = None`. Lors d'un fragment rerun, `record_if_active()` fait deja un NO-OP
> naturel car `_collector is None`. Le guard est conserve comme filet de securite au cas
> ou l'ordre d'execution changerait dans le futur.

---

### Sprint 3 : Envelopper les blocs dans `st.fragment` (1 fichier modifie)

#### Etape 3.1 : Modifier la boucle continue dans `streamtex/book.py`

**Lignes impactees** : 192-215

**Avant** :
```python
for i, module in enumerate(module_list):
    if use_toc_block and i == toc_pos:
        toc_block = st_toc(toc_title_style)
    if collector is not None:
        collector.set_block(i)
    toc_before = len(toc_entries()) if use_toc_sidebar else 0

    st_include(module, *args, _inspector_config=inspector, **kwargs)

    if use_toc_sidebar:
        for entry in toc_entries()[toc_before:]:
            if "block_idx" not in entry:
                entry["block_idx"] = i
    if separator and i < len(module_list) - 1:
        st_include(separator, *args, **kwargs)
    st_space("v", "70px")
```

**Apres** :
```python
for i, module in enumerate(module_list):
    if use_toc_block and i == toc_pos:
        toc_block = st_toc(toc_title_style)
    if collector is not None:
        collector.set_block(i)
    toc_before = len(toc_entries()) if use_toc_sidebar else 0

    # Wrap block rendering in st.fragment for O(1) widget reruns.
    # The fragment_guard module prevents global registry mutations
    # during fragment reruns (TOC, markers, export, search).
    _render_block_fragment = st.fragment(_make_block_renderer(
        module, args, kwargs, inspector,
    ))
    _render_block_fragment()

    if use_toc_sidebar:
        for entry in toc_entries()[toc_before:]:
            if "block_idx" not in entry:
                entry["block_idx"] = i
    if separator and i < len(module_list) - 1:
        st_include(separator, *args, **kwargs)
    st_space("v", "70px")
```

**Fonction helper a ajouter** dans `book.py` :
```python
def _make_block_renderer(
    module, args: tuple, kwargs: dict, inspector_config
):
    """Create a closure that renders a single block.

    This closure is passed to st.fragment() so that widget interactions
    inside the block only trigger a partial rerun of this block.
    The fragment_guard module (consulted by toc.py, marker.py, export.py,
    search.py) ensures global registries are not mutated during the
    fragment rerun.
    """
    def _render():
        st_include(module, *args, _inspector_config=inspector_config, **kwargs)
    return _render
```

**Pourquoi une closure** : `st.fragment()` attend un callable sans argument. La closure capture `module`, `args`, `kwargs`, `inspector_config` par fermeture lexicale. Chaque iteration de la boucle cree une closure distincte, donc un fragment distinct.

**Pourquoi le code hors-fragment reste inchange** : Les operations `collector.set_block(i)`, `toc_before`, le tagging TOC `entry["block_idx"] = i`, les separateurs et les espacements s'executent dans le scope de `st_book()`, PAS dans le fragment. Lors d'un fragment rerun, seul `_render_block_fragment()` re-execute — le code de la boucle `st_book()` ne re-execute PAS (c'est le comportement standard de `st.fragment`).

#### Etape 3.2 : Gestion du bouton Inspector dans le fragment

**Probleme** : Le bouton "Edit" (rendu par `render_edit_button()` dans `st_include()`) est a l'interieur du fragment. Un clic met a jour `st.session_state[_STX_INSPECTOR_OPEN]`, mais le panel Inspector (rendu hors fragment) ne se met pas a jour.

**Solution** : Ajouter `st.rerun(scope="app")` dans `st_include()` apres detection du clic Inspector, suivant le pattern deja utilise dans `inspector.py` (l.831).

**Lignes impactees** : `book.py` l.393-416 (`st_include`)

**Apres** (ajout a la fin de `st_include`) :
```python
def st_include(block_file_module, *args, _inspector_config=None, **kwargs):
    # ... code existant inchange ...
    try:
        block_file_module.build(*args, **kwargs)
    except Exception as e:
        st.markdown(f":red-background[Error in block '{module_name}': {e}]")
        raise

    # If the inspector edit button was clicked inside a fragment,
    # trigger a full app rerun so the inspector panel updates.
    if _inspector_config and _inspector_config.enabled:
        if st.session_state.pop("_stx_inspector_needs_rerun", False):
            st.rerun(scope="app")
```

---

### Sprint 4 : Tests

#### Etape 4.1 : Tests unitaires pour `fragment_guard.py`

**Nouveau fichier** : `tests/test_fragment_guard.py`

```python
"""Tests for fragment_guard module."""

from streamtex.fragment_guard import is_fragment_rerun


def test_is_fragment_rerun_outside_streamlit():
    """Outside Streamlit, should always return False."""
    assert is_fragment_rerun() is False


def test_is_fragment_rerun_no_context(monkeypatch):
    """With get_script_run_ctx returning None, should return False."""
    import streamtex.fragment_guard as fg
    monkeypatch.setattr(
        "streamlit.runtime.scriptrunner_utils.script_run_context.get_script_run_ctx",
        lambda: None,
    )
    assert fg.is_fragment_rerun() is False
```

#### Etape 4.2 : Tests unitaires pour les guards sur les registres

**Fichiers existants a modifier** : `tests/test_toc.py`, `tests/test_marker.py`, `tests/test_export.py`, `tests/test_search.py`

Pour chaque registre, ajouter un test qui :
1. Remplit le registre normalement (simule full rerun)
2. Monkeypatche `is_fragment_rerun` pour retourner `True`
3. Appelle la fonction de mutation
4. Verifie que le registre n'a PAS ete modifie (pas de doublons)
5. Verifie que la valeur de retour est correcte (ancre existante pour TOC, index existant pour markers)

Exemple pour TOC :
```python
def test_register_toc_entry_skipped_during_fragment_rerun(monkeypatch):
    """During fragment rerun, register_toc_entry should not add duplicates."""
    reset_toc_registry()
    key_anchor, section_number, lvl = register_toc_entry("Section A", "1")
    assert len(toc_entries()) == 1

    # Simulate fragment rerun
    monkeypatch.setattr(
        "streamtex.toc.is_fragment_rerun", lambda: True
    )
    key_anchor2, section_number2, lvl2 = register_toc_entry("Section A", "1")
    assert len(toc_entries()) == 1         # No duplicate
    assert key_anchor2 == key_anchor       # Same anchor
    assert section_number2 == section_number  # Same numbering
    assert lvl2 == lvl                     # Same level
```

#### Etape 4.3 : Test d'integration manuelle

**Tests fonctionnels** :

| Scenario | Verification |
|----------|-------------|
| Projet intro (9 blocs), mode continu | Tous les blocs s'affichent normalement au chargement initial |
| Clic sur un widget dans un bloc (ex: expander) | Seul ce bloc se re-rend (verifier via `print()` temporaire dans `build()`) |
| TOC sidebar apres clic widget | Pas de doublons, numerotation correcte, ancres fonctionnelles |
| Navigation markers apres clic widget | Widget flottant inchange, PageUp/PageDown fonctionnel |
| Recherche texte apres clic widget | Resultats corrects, pas de doublons |
| Export HTML apres clic widget | Export complet, pas de contenu duplique (voir limitation connue L1) |
| Bouton Inspector dans un bloc | Le panel s'ouvre (full rerun declenche via `scope="app"`) |
| Changement View mode (Paginated/Continuous) | Full rerun, tout se reconstruit normalement |
| Changement Zoom/Width sidebar | Full rerun, tout se re-rend normalement |

**Tests visuels (effets de bord)** :

| Scenario | Verification |
|----------|-------------|
| Bloc avec diagramme Mermaid + widget | Apres clic widget, le diagramme flash (iframe recree). Etat pan/zoom perdu |
| Bloc avec diagramme PlantUML + widget | Meme comportement que Mermaid |
| Bloc avec wizard `st.rerun()` (bck_dynamic_content) | Boutons Previous/Next fonctionnent (fragment rerun suffit pour ce cas) |
| Scroll position apres clic widget | La position de scroll ne bouge pas |
| Interactions rapides sur 2 blocs differents | Les deux blocs se re-rendent sequentiellement, pas de crash |
| Bloc composite (3 sous-blocs) + widget dans un sous-bloc | Les 3 sous-blocs se re-rendent (isolation au niveau composite, pas atomique) |

---

## 5. Fichiers impactes

### Fichiers nouveaux

| Fichier | Description | Lignes estimees |
|---------|-------------|-----------------|
| `streamtex/fragment_guard.py` | Module central de detection fragment rerun | ~25 |
| `tests/test_fragment_guard.py` | Tests unitaires du guard | ~30 |

### Fichiers modifies

| Fichier | Modification | Lignes impactees |
|---------|-------------|-----------------|
| `streamtex/toc.py` | Champ `_section_number` dans entries (l.88-94) + guard dans `register_toc_entry()` (l.122-131) + helper `_find_existing_toc_entry()` retournant un 3-tuple | l.88-94, l.122-131, +20 lignes |
| `streamtex/marker.py` | Guard dans `register_marker()` + helper `_find_existing_marker_index()` | l.87-93, +12 lignes |
| `streamtex/export.py` | Guard dans `st_html()`, `export_append()`, `export_push_wrapper()`, `export_pop_wrapper()` | l.145-160, l.224-227, ~12 lignes |
| `streamtex/search.py` | Guard dans `record_if_active()` | l.55-57, +3 lignes |
| `streamtex/book.py` | Wrapper `st.fragment` dans la boucle continue + helper `_make_block_renderer()` + rerun Inspector | l.192-215, l.393-416, +20 lignes |

### Fichiers NON modifies

- Tous les fichiers `bck_*.py` (blocs) — **zero changement**
- `streamtex/container.py`, `streamtex/grid.py`, `streamtex/list.py` — les context managers n'ont pas besoin de guard car `export_push/pop_wrapper` sont deja guardes dans `export.py`
- `streamtex/write.py` — appelle `register_toc_entry()` qui est deja guarde
- `streamtex/styles/` — aucun etat global
- `streamtex/bib.py` — `cite()` est deja idempotent

### Total estime

- **~130 lignes de code ajoutees/modifiees** dans la librairie (inclut le champ `_section_number` et le 3-tuple)
- **~70 lignes de tests** (inclut les tests du 3-tuple)
- **6 fichiers modifies** + **2 fichiers nouveaux**

---

## 6. Tests

### Strategie

```
Tests unitaires (automatises, pytest)
  ├── test_fragment_guard.py       → detection fragment rerun
  ├── test_toc.py (ajouts)         → guard TOC, pas de doublons
  ├── test_marker.py (ajouts)      → guard markers, pas de doublons
  ├── test_export.py (ajouts)      → guard export buffer, pas d'append
  └── test_search.py (ajouts)      → guard search collector, pas de record

Tests d'integration (manuels)
  ├── Projet intro, mode continu   → verification visuelle
  ├── Projet advanced, mode continu → verification visuelle
  └── Collection, mode continu      → verification visuelle
```

### Commandes

```bash
# Tests unitaires
uv run pytest tests/test_fragment_guard.py -v
uv run pytest tests/test_toc.py tests/test_marker.py tests/test_export.py tests/test_search.py -v

# Suite complete
uv run pytest tests/ -v

# Lint
uv run ruff check streamtex/

# Test d'integration manuelle
uv run streamlit run documentation/manuals/stx_manual_intro/book.py
uv run streamlit run documentation/manuals/stx_manual_advanced/book.py
```

---

## 7. Risques et mitigations

### Risque 1 : API interne Streamlit (`get_script_run_ctx`)

**Description** : La detection du fragment rerun utilise `streamlit.runtime.scriptrunner_utils.script_run_context.get_script_run_ctx`, qui est une API interne non documentee dans le contrat public de Streamlit. Elle pourrait changer dans une version future.

**Probabilite** : Faible. Cette API est stable depuis Streamlit 1.0 et utilisee par de nombreuses librairies tierces (streamlit-extras, streamlit-option-menu, etc.).

**Mitigation** :
- Le `try/except ImportError` dans `fragment_guard.py` protege contre un changement de chemin d'import
- Si l'API disparait, `is_fragment_rerun()` retourne `False` → comportement identique a aujourd'hui (pas de guard, full rerun partout)
- Ajouter un test qui detecte un changement d'API a chaque mise a jour de Streamlit :

```python
def test_streamlit_context_api_available():
    """Verify the internal API we depend on still exists."""
    from streamlit.runtime.scriptrunner_utils.script_run_context import (
        get_script_run_ctx,
    )
    assert callable(get_script_run_ctx)
```

### Risque 2 : Entrees TOC introuvables lors du fragment rerun

**Description** : Si `_find_existing_toc_entry(label)` ne trouve pas l'entree dans le registre (ex: label different entre deux rendus, entree supprimee), elle retourne un 3-tuple par defaut `(slug, "", 1)` qui pourrait differer de l'ancre originale.

**Probabilite** : Tres faible. Les labels sont des constantes codees en dur dans les blocs (`st_write(style, "Mon Titre", toc_lvl="1")`). L'analyse des 90+ blocs confirme que tous les `toc_lvl` sont inconditionnels.

**Mitigation** : Le fallback utilise `TOCRegistry.get_key_anchor(label)` (meme logique de slugification que lors du full rerun), ce qui produit un resultat identique. Si deux entrees ont le meme label, la premiere correspondance est retournee (coherent avec le rendu sequentiel du full rerun).

### Risque 3 : Performance du guard (appel `is_fragment_rerun()` frequent)

**Description** : `is_fragment_rerun()` est appele pour chaque appel a `st_html()`, `register_toc_entry()`, `register_marker()`, `record_if_active()`, `export_append/push/pop`. Pour un bloc avec 50 appels `st_write`, cela fait ~50 appels a `get_script_run_ctx()`.

**Probabilite** : Impact negligeable. `get_script_run_ctx()` est un simple lookup dans un `threading.local()` — O(1), ~100ns par appel. Pour 50 appels, c'est ~5us de surcharge.

**Mitigation** : Si necessaire, cacher le resultat dans un `ContextVar` initialise une fois par rerun. Pas necessaire en v1.

### Risque 4 : Fragment rerun + st.rerun(scope="app")

**Description** : Si un bloc appelle `st.rerun(scope="app")` (ex: bouton Inspector), le full rerun qui suit va re-executer `st_book()` depuis le debut, y compris les `reset_*_registry()`. Ce full rerun va reconstruire tous les registres normalement.

**Probabilite** : Certain (c'est le comportement attendu).

**Mitigation** : Aucune necessaire. C'est le comportement correct — le full rerun reconstruit tout proprement.

### Risque 5 : Blocs composites avec `st_include` interne

**Description** : Un bloc composite (ex: `bck_text_and_styling.py`) appelle `st_include()` pour ses sous-blocs atomiques. Les 3 sous-blocs sont dans le meme fragment. Un widget dans un sous-bloc re-rend les 3 sous-blocs.

**Probabilite** : Certain.

**Mitigation** : Comportement acceptable. Le gain principal (ne pas re-rendre les N-1 autres blocs du livre) est preserve. L'isolation plus fine (par sous-bloc) serait une optimisation future.

### Risque 6 : Flash visuel des iframes (diagrammes) lors du fragment rerun

> **Ajoute en v2.0**

**Description** : Les diagrammes (Mermaid, PlantUML, TikZ) sont rendus dans des `<iframe>` via `components.html()`. Lors d'un fragment rerun, l'iframe est **detruit puis recree** (comportement natif Streamlit). L'utilisateur voit un flash blanc de 100-500ms et l'etat pan/zoom est perdu.

**Probabilite** : Ne se produit QUE si un bloc contient a la fois un diagramme ET un widget interactif. Aucun bloc actuel n'a ce pattern (les blocs de diagrammes sont purement visuels).

**Impact** : Haute si le pattern existe, mais inexistant dans le codebase actuel.

**Mitigation** :
- Court terme : accepter (aucun bloc actuel n'est affecte)
- Moyen terme : option `fragment=False` sur `st_include()` pour exclure certains blocs du wrapping
- Long terme : sauvegarder l'etat pan/zoom dans `st.session_state` et le restaurer apres le rerun

### Risque 7 : `st.rerun()` dans un fragment declenche un fragment rerun, pas un full rerun

> **Ajoute en v2.0**

**Description** : `bck_dynamic_content.py` utilise `st.rerun()` dans des callbacks de boutons (wizard Previous/Next/Reset). Depuis l'interieur d'un fragment, `st.rerun()` sans argument declenche un **fragment rerun** (pas un full rerun). Le wizard fonctionnerait (il ne modifie que son propre affichage via `st.session_state.bck30_step`), mais un concepteur futur pourrait s'attendre a un full rerun.

**Probabilite** : Le bloc actuel fonctionne correctement. Le risque concerne les futurs blocs.

**Mitigation** : Documenter dans `coding_standards.md` que `st.rerun()` dans un bloc en mode continu declenche un fragment rerun. Utiliser `st.rerun(scope="app")` si un full rerun est necessaire.

### Risque 8 : Layout shift lors du changement de hauteur d'un bloc

> **Ajoute en v2.0**

**Description** : Quand un fragment rerun modifie la hauteur d'un bloc (ex: expander qui s'ouvre), le contenu en dessous se decale verticalement. Si le bloc est au-dessus de la zone visible, le viewport peut sauter brievement.

**Probabilite** : Certain pour les blocs avec expanders/toggles qui changent la hauteur.

**Mitigation** : C'est le comportement identique a aujourd'hui (un expander qui s'ouvre cause deja un shift en full rerun). Pas de degradation supplementaire.

---

## 8. Effets de bord visuels pour l'utilisateur final

> **Section ajoutee en v2.0** apres analyse approfondie des effets visuels.

### Aucun probleme

| Aspect | Raison |
|--------|--------|
| **Position de scroll** | Preservee nativement par Streamlit lors des fragment reruns. Le fragment ne modifie que son propre conteneur dans le DOM. |
| **Etat des widgets** (sliders, selectbox, etc.) | Preserves via `st.session_state` avec cles stables. Tous les blocs existants utilisent des cles explicites prefixees (ex: `bck26_counter`). |
| **Espacements 70px entre blocs** | Rendus hors fragment dans la boucle `st_book()`, jamais re-executes lors d'un fragment rerun. |
| **TOC sidebar** | Pas de re-rendu, pas de doublons. Le guard empeche les re-enregistrements. |
| **Conteneur `st.container()` supplementaire** | `st.fragment` cree un div wrapper invisible (pas de border, margin, padding). Aucun impact visuel. |

### Effets mineurs

| Effet | Severite | Detail |
|-------|----------|--------|
| **Micro-flash CSS (FOUC theorique)** | Negligeable | `st_block()` genere un nouvel UUID a chaque rerun. L'ancien `<style>` est supprime et le nouveau est injecte. Fenetre sans style : ~16ms (1 frame navigateur). Imperceptible. |
| **Indicateur de chargement** | Faible | Streamlit affiche un leger "greying out" des elements du fragment pendant le rerun. Pas de spinner explicite. |

### Effets significatifs (contextuels)

| Effet | Severite | Condition de declenchement | Detail |
|-------|----------|---------------------------|--------|
| **Flash diagrammes** | Haute | Bloc avec diagramme + widget interactif | L'iframe est detruit/recree. Flash blanc 100-500ms. Etat pan/zoom perdu. **Aucun bloc actuel n'a ce pattern.** |
| **Perte navigation markers** | Faible | Bloc avec marqueur re-rendu | Le `<div>` marqueur est recree avec le meme anchor ID. Le JS de scroll tracking (debounce 150ms) rattrape le changement automatiquement. |
| **Reruns multiples rapides** | Faible | Clics rapides sur widgets de blocs differents | Les fragments s'executent sequentiellement (pas de concurrence). Chaque bloc flash/re-rend dans l'ordre. Visuellement saccade mais fonctionnellement correct. |

---

## 9. Contraintes pour les futurs concepteurs de blocs

> **Section ajoutee en v2.0.** A integrer dans `documentation/coding_standards.md` lors de l'implementation.

### Contrainte C1 : Ne pas utiliser `toc_lvl` ou `st_marker()` conditionnellement

**Interdit** :
```python
def build():
    if st.toggle("Show advanced"):
        st_write(style, "Advanced Section", toc_lvl="2")  # INTERDIT
```

**Raison** : Lors d'un fragment rerun, `register_toc_entry()` est un NO-OP. L'entree TOC ne serait jamais ajoutee. La section serait rendue visuellement mais absente de la TOC.

**Pattern correct** : Toujours placer les `toc_lvl` et `st_marker()` de facon inconditionnelle, en debut de section. Utiliser les widgets pour controler le contenu *sous* le titre, pas le titre lui-meme.

**Verification** : Tous les 90+ blocs existants respectent deja cette contrainte (toc_lvl est toujours inconditionnel).

### Contrainte C2 : Utiliser `st.rerun(scope="app")` pour un full rerun

**Attention** :
```python
def build():
    if st.button("Reload everything"):
        st.rerun()             # ← fragment rerun seulement !
        st.rerun(scope="app")  # ← full rerun (correct)
```

**Raison** : En mode continu, chaque bloc est enveloppe dans un `st.fragment`. Un appel `st.rerun()` sans argument depuis `build()` declenche un fragment rerun (seul ce bloc est re-execute), pas un full rerun de la page.

**Bloc existant concerne** : `bck_dynamic_content.py` utilise `st.rerun()` pour un wizard. Le wizard fonctionne correctement car il ne modifie que son propre etat (`st.session_state.bck30_step`). Pas de correction requise.

### Contrainte C3 : Citations conditionnelles et bibliographie

**Cas limite** :
```python
def build():
    if st.toggle("Show references"):
        st_cite("key_2024")  # ← ajoutera la citation au registre, mais st_bibliography()
                              #   (rendu dans un autre bloc) ne sera pas re-execute.
```

**Impact** : Le numero de citation apparait dans le texte, mais l'entree correspondante dans la bibliographie n'est visible qu'apres un full rerun (changement de zoom, refresh page, etc.).

**Pattern correct** : Placer `st_cite()` inconditionnellement. Utiliser les widgets pour controler l'affichage du texte *autour* de la citation, pas la citation elle-meme.

---

## 10. Limitations connues

> **Section ajoutee en v2.0.** Ces limitations sont des compromis acceptes.

### L1 : Export HTML reflete le dernier full rerun

Apres des interactions widget (fragment reruns), le bouton "Download HTML" produit le HTML du **dernier full rerun**, pas l'etat visuel courant. Si un widget a change du contenu visible (ex: toggle, selectbox), l'export ne reflecte pas ces changements.

**Contournement** : Changer le zoom, le mode (Paginated/Continuous), ou rafraichir la page pour declencher un full rerun avant d'exporter.

**Raison technique** : Le buffer d'export est guarde pendant les fragment reruns pour eviter la corruption (doublons, stack desynchronisee). Accepter l'export "stale" est le compromis le moins risque.

### L2 : Index de recherche reflete le dernier full rerun — RESOLU

Meme principe que L1. Si un widget montre/cache du contenu dans un bloc, l'index de recherche ne reflete pas le changement visuel.

**Resolution** : Un bouton "Refresh search index" a ete ajoute dans la sidebar (au-dessus des onglets TOC/Markers), en mode pagine et en mode continu. En mode continu, le bouton declenche un `st.rerun()` qui reconstruit l'index. En mode pagine, il supprime egalement le cache (`_stx_page_cache`) pour forcer `_build_page_cache()` a se re-executer.

**Impact reel** : Tres faible. La recherche StreamTeX opere au niveau bloc (montre/cache des blocs entiers par index). Le contenu conditionnel intra-bloc ne change pas la presence du bloc dans les resultats.

### L3 : Blocs composites : isolation au niveau composite, pas atomique

Un bloc composite qui inclut 3 sous-blocs atomiques est un seul fragment. Un widget dans un sous-bloc atomique re-rend les 3 sous-blocs (pas seulement le sous-bloc concerne).

**Impact** : Le gain principal (ne pas re-rendre les N-1 autres blocs du livre) est preserve. Seule l'isolation intra-composite est perdue.

---

## 11. Criteres de validation

### Criteres fonctionnels (MUST)

- [ ] Chargement initial d'un projet en mode continu : identique a aujourd'hui
- [ ] TOC sidebar : aucun doublon apres interaction widget dans un bloc
- [ ] Numerotation TOC : correcte apres interaction widget (3-tuple verifie)
- [ ] Markers : aucun doublon, indices corrects apres interaction widget
- [ ] Navigation markers (PageUp/PageDown) : fonctionnelle apres interaction widget
- [ ] Recherche textuelle : resultats corrects, pas de doublons
- [ ] Export HTML : contenu complet et correct (reflete le dernier full rerun, cf. limitation L1)
- [ ] Bouton Inspector : ouvre le panel (declenche full rerun via `scope="app"`)
- [ ] Widgets sidebar (Zoom, Width, View mode) : declenchent full rerun normalement
- [ ] Tous les 203+ tests existants passent
- [ ] Wizard Previous/Next/Reset (`bck_dynamic_content`) fonctionne dans le fragment

### Criteres de performance (SHOULD)

- [ ] Interaction widget dans un bloc : rerun < 500ms (au lieu de N * temps_bloc)
- [ ] Pas de regression sur le temps de chargement initial
- [ ] Pas de fuite memoire DOM (verifier DevTools apres 20 interactions)

### Criteres visuels (SHOULD)

- [ ] Scroll position preservee apres interaction widget dans un bloc
- [ ] Pas de flash visible sur les blocs sans diagramme ni iframe
- [ ] Espacements entre blocs stables (pas de layout jump)

### Criteres de compatibilite (MUST)

- [ ] Zero changement dans le code des blocs existants
- [ ] Mode pagine non impacte (le guard n'intervient que dans la boucle continue)
- [ ] `uv run ruff check streamtex/` sans erreur

### Documentation a mettre a jour (SHOULD)

- [ ] `documentation/coding_standards.md` : ajouter contraintes C1, C2, C3
- [ ] `CLAUDE.md` : mentionner le fragment guard dans la section "Key Components"
