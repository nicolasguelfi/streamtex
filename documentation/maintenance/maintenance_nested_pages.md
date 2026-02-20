# Proposition : Support des listes imbriquees dans st_book() pour le mode pagine

**Date** : 2026-02-20
**Statut** : Proposition (non implemente)
**Priorite** : Moyenne

---

## Contexte

En mode pagine (`paginate=True`), chaque element de `module_list` dans `st_book()` correspond a exactement **une page**. Il n'existe pas de mecanisme pour regrouper plusieurs blocs sur une meme page.

### Solution temporaire actuelle

Les blocs qui doivent apparaitre ensemble utilisent `st_include()` en interne :

```python
# bck_level_badge.py — charge et inclut le header partage
import importlib.util
from streamtex import st_include

_header = ...  # charge via importlib.util
def build():
    st_include(_header)          # header partage
    # ... badge local ...        # sur la meme page
```

Cette approche fonctionne mais ne permet pas de controler le regroupement depuis `book.py`.

---

## Proposition : Listes imbriquees

### Syntaxe

```python
st_book([
    [shared_blocks.bck_header, blocks.bck_level_badge],  # meme page
    blocks.bck_installation,                               # page separee
    blocks.bck_new_project,                                # page separee
    [blocks.bck_summary, shared_blocks.bck_footer],       # meme page
], paginate=True)
```

- **Element simple** (module) : une page dediee (comportement actuel, inchange)
- **Liste/tuple** : tous les modules du groupe sont rendus sequentiellement sur la meme page

### Avantages

1. Le regroupement est declare dans `book.py`, pas cache dans les blocs
2. Les blocs restent des fichiers independants et reutilisables
3. Retro-compatible : une liste plate fonctionne exactement comme avant

---

## Analyse d'impact sur le code

### Fichier : `streamtex/book.py`

#### 1. `_compute_cache_hash(module_list)` (ligne 244)

**Actuel** :
```python
names = "|".join(getattr(m, '__name__', str(m)) for m in module_list)
```

**Modification** : Aplatir les groupes pour le hash.
```python
def _flatten_name(item):
    if isinstance(item, (list, tuple)):
        return "[" + ",".join(getattr(m, '__name__', str(m)) for m in item) + "]"
    return getattr(item, '__name__', str(item))

names = "|".join(_flatten_name(m) for m in module_list)
```

**Risque** : Faible. Le hash change si la composition change, ce qui invalide le cache correctement.

---

#### 2. `_build_page_cache(module_list, ...)` (ligne 276)

**Actuel** :
```python
for i, module in enumerate(module_list):
    st_include(module, *args, **kwargs)
    # Tag entries with page_idx = i
```

**Modification** :
```python
for i, item in enumerate(module_list):
    modules = item if isinstance(item, (list, tuple)) else [item]
    for module in modules:
        st_include(module, *args, **kwargs)
    # Tag entries with page_idx = i  (inchange)
```

**Risque** : Faible. Le `page_idx` reste `i` (l'index dans module_list). Tous les modules d'un groupe partagent le meme `page_idx`, donc les entrees TOC et marqueurs sont correctement associees a la meme page.

**Point d'attention** : Le separateur (`separator`) ne doit pas etre insere entre les modules d'un meme groupe, seulement entre les groupes/pages.

---

#### 3. `_paginated_book(module_list, ...)` (ligne 669)

**Actuel** (ligne 749) :
```python
st_include(module_list[current_page], *args, **kwargs)
```

**Modification** :
```python
item = module_list[current_page]
modules = item if isinstance(item, (list, tuple)) else [item]
for module in modules:
    st_include(module, *args, **kwargs)
```

**Risque** : Faible. Le rendu sequentiel de plusieurs modules dans le meme container Streamlit est le meme mecanisme que le mode continu.

---

#### 4. `_get_page_titles(cache, total)` (ligne 250)

**Aucune modification necessaire.** Cette fonction utilise `page_idx` depuis le cache. Comme les TOC entries d'un groupe partagent le meme `page_idx`, le premier titre TOC du groupe sera utilise comme titre de page. C'est le comportement souhaite.

---

#### 5. `_preseed_toc_registry(cached_toc, current_page)` (ligne 260)

**Aucune modification necessaire.** Cette fonction itere sur les entrees TOC cachees et filtre par `page_idx`. Les groupes n'affectent pas cette logique car `page_idx` est deja correctement attribue dans `_build_page_cache`.

---

#### 6. `_build_paginated_sidebar(cache, ...)` (ligne 315)

**Aucune modification necessaire.** La sidebar utilise `page_idx` pour generer les liens. Les entrees TOC/marqueurs d'un groupe ont le meme `page_idx`, donc elles pointent vers la meme page.

---

#### 7. Monties (bannieres prev/next) (lignes 737-768)

**Aucune modification necessaire.** Les Monties utilisent `page_titles[current_page +/- 1]`, qui est derive de `_get_page_titles`. Le `total` reste `len(module_list)`, ce qui est correct puisque chaque element (simple ou groupe) est une page.

---

#### 8. Boutons de navigation caches (ligne 790)

**Aucune modification necessaire.** Le `range(total)` itere sur les pages (pas les modules). Chaque page a un bouton, que ce soit un module simple ou un groupe.

---

#### 9. `_inject_paginated_nav_js(...)` (ligne 380)

**Aucune modification necessaire.** Le JS recoit `currentPage` et `totalPages` qui correspondent aux index de `module_list`. La logique reste identique.

---

#### 10. Mode continu (lignes 93-107)

**Actuel** :
```python
for i, module in enumerate(module_list):
    st_include(module, *args, **kwargs)
```

**Modification** :
```python
for i, item in enumerate(module_list):
    modules = item if isinstance(item, (list, tuple)) else [item]
    for module in modules:
        st_include(module, *args, **kwargs)
```

**Risque** : Faible. En mode continu, tous les modules sont rendus sequentiellement. Le resultat visuel est identique.

---

## Resume des modifications

| Fonction | Modifiee | Risque |
|----------|----------|--------|
| `_compute_cache_hash` | Oui | Faible |
| `_build_page_cache` | Oui | Faible |
| `_paginated_book` (render) | Oui | Faible |
| `_get_page_titles` | Non | - |
| `_preseed_toc_registry` | Non | - |
| `_build_paginated_sidebar` | Non | - |
| Monties (bannieres) | Non | - |
| Boutons navigation | Non | - |
| JS pagination | Non | - |
| Mode continu | Oui | Faible |

**Total : 4 fonctions a modifier, 0 risque eleve.**

---

## Points de vigilance

1. **Separateur entre groupes** : Le `separator` ne doit etre insere qu'entre les pages (groupes), pas entre les modules d'un meme groupe. Verifier la logique `if separator and i < len(module_list) - 1`.

2. **`st_include` et erreurs** : Si un module d'un groupe echoue, les modules suivants du meme groupe ne seront pas rendus (le `raise` dans `st_include` interrompt le groupe). C'est le comportement souhaite car un groupe est une unite logique.

3. **Export HTML** : En mode export, les modules d'un groupe sont rendus sequentiellement dans le buffer. Pas de modification necessaire.

4. **Cache invalidation** : Le hash doit distinguer `[A, B]` (2 pages) de `[[A, B]]` (1 page). La fonction `_flatten_name` modifiee gere cela avec les crochets dans la representation.

5. **Tests unitaires** : Ajouter des tests pour :
   - `_compute_cache_hash` avec groupes
   - `_build_page_cache` : verifier que les `page_idx` sont identiques pour les modules d'un groupe
   - Rendu pagine avec groupes : verifier que les modules d'un groupe apparaissent sur la meme page

---

## Estimation

- **Complexite** : Faible (4 modifications mineures + tests)
- **Retro-compatibilite** : 100% (les listes plates fonctionnent sans changement)
- **Tests existants** : Aucun test unitaire ne couvre le mode pagine actuellement (les 203 tests portent sur les composants individuels)
