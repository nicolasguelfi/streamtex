# 📚 Aide-mémoire Complet Streamtex

## 📥 Importations Essentielles

```python
from streamtex import *
from streamtex.styles import Style as ns, StyleGrid as sg
from streamtex.enums import Tags as t, ListTypes as lt

```

## 🎨 Organisation des Styles

### Classe de Style Personnalisée

```python
class BlockStyles:
    """Styles personnalisés définis localement et utilisés uniquement pour ce bloc"""
    # Styles composés
    content = s.Large + s.center_txt
    lime_bold = s.text.colors.lime + s.bold
    bold_green = s.project.colors.green_01 + s.bold
    
    # Styles avec alignement
    green_title = bold_green + s.huge + s.center_txt
    
    # Styles avec bordures
    border = s.container.borders.color(s.text.colors.black) + \
             s.container.borders.solid_border + \
             s.container.borders.size("2px")
    
    # Styles avec padding (remplissage)
    side_padding = ns("padding: 10pt 36pt;")
bs = BlockStyles

```

## 📝 Éléments de Base

### Blocs et Texte

```python
# Bloc simple avec style
with st_block(s.center_txt):
    st_write(bs.green_title, "Mon Titre")
    st_space(size=3)

# Bloc avec liste
with st_block(s.center_txt):
    with st_list(
        list_type=l.ordered,
        li_style=bs.content) as l:
        with l.item(): st_write("Premier élément")
        with l.item(): st_write("Deuxième élément")


```

### Images et Médias

```python
# Image simple
st_image(uri="image.png")

# Image avec dimensions
st_image(uri="image.png", width="1150px", height="735.34px")

# Image avec lien
st_image(uri="image.png", link="[https://example.com](https://example.com)")

# Image avec style hauteur automatique
st_image(s.container.sizes.height_auto, uri="image.png")

```

### Grilles et Tableaux

```python
# Grille à 2 colonnes de largeur égale
with st_grid(
    cols=2, 
    cell_styles=bs.border + s.container.paddings.little_padding
    ) as g:
    # rangée 1
    with g.cell(): st_image(uri="image1.png")
    with g.cell(): st_image(uri="image2.png")
    # rangée 2
    with g.cell(): st_image(uri="image3.png")


# Grille (tableau) avec styles de grille personnalisés
with st_grid(
    cols=2, 
    cell_styles=sg.create("A1,A3", s.project.colors.orange_02) +
                sg.create("A2", s.project.colors.red_01) +
                sg.create("A1:B3", s.bold + s.LARGE)
    ) as g:
    # rangée 1
    with g.cell(): st_write("Titre")
    with g.cell(): st_write("Lien")
    # rangée 2
    with g.cell(): st_write("Élément 1")
    with g.cell(): st_write("lien1")
    # rangée 3
    with g.cell(): st_write("Élément 2")
    with g.cell(): st_write("lien2")

```

## 🔗 Liens et Navigation

### Liens

```python
# Lien simple
st_write("Cliquez ici", link="[https://example.com](https://example.com)")

# Lien stylisé
link_style = s.text.colors.blue + s.text.decors.underline_text
st_write(link_style, "Lien stylisé", link="[https://example.com](https://example.com)", no_link_decor=True)

```

### Table des Matières

```python
# Niveau supérieur
st_write(style, "Section", toc_lvl="1")

# Sous-niveau
st_write(style, "Sous-section", toc_lvl="+1")

# TOCConfig avec filtrage de la sidebar
toc = TOCConfig(
    numerate_titles=False,
    toc_position=0,
    sidebar_max_level=None,  # None = auto (paginé: 1, continu: 2)
)
```

## 🎯 Styles Prédéfinis

### Couleurs

```python
# Couleurs du projet
s.project.colors.blue_01
s.project.colors.green_01
s.project.colors.orange_01
s.project.colors.red_01
s.project.colors.brown_01

# Couleurs du texte
s.text.colors.lime
s.text.colors.black

```

### Tailles de Texte

```python
s.huge          # Très grand
s.LARGE         # Plus grand
s.Large         # Grand
s.large         # Normal

```

### Alignement et Mise en page

```python
s.center_txt
s.container.flex.center_align_items
s.container.layouts.vertical_center_layout

```

### Décorations

```python
s.bold
s.italic
s.text.decors.underline_text

```

## 🔧 Utilitaires

### Espacement

```python
# Espace vertical
st_space(size=3)
st_space("v", size=2)

# Espace horizontal
st_space("h", size=1)

# Saut de ligne
st_br()

```

### Conteneurs

```python
# Padding (Remplissage)
s.container.paddings.little_padding
s.container.paddings.small_padding

# Bordures
s.container.borders.solid_border
s.container.borders.size("2px")

```

## 💡 Exemples Complets

### Page de Documentation

```python
def build():
    with st_block(bs.center_txt):
        st_write(bs.green_title, "Documentation")
        st_space(size=3)
        with st_list(l.ordered, bs.content) as l:
            with l.item(): st_write("Premier point")
            with l.item(): st_write("Deuxième point")

```

### Vitrine avec Grille

```python
def build():
    ### Grille à 2 colonnes
    st_grid(
        cols=2, 
        cell_styles=bs.border) as g:
        with g.cell(): st_image(uri="image1.png")
        with g.cell(): st_image(uri="image2.png")
        with g.cell(): st_write(bs.content, "Description")

```

### Exemple de Page Complète

```python
def build():
    # En-tête avec titre
    with st_block(s.center_txt + s.LARGE + s.bold):
        st_write(s.project.colors.blue_01 + s.huge, "Titre Principal", toc_lvl="1")
        st_space(size=2)
        st_write(s.project.colors.orange_01, "Sous-titre", toc_lvl="+1")
        st_space(size=3)

    # Contenu principal
    with st_block(s.center_txt):
        with st_list(
            list_type=l.ordered,
            li_style=bs.content) as l:
            with l.item(): st_write("Section 1")
            with l.item(): st_write("Section 2")
            with l.item(): st_write("Section 3")

    # Grille d'images
    st_grid(
        cols=2,
        cell_styles=bs.border + s.container.paddings.little_padding) as g:
            with g.cell(): st_image(uri="image1.png")
            with g.cell(): st_image(uri="image2.png")
            with g.cell(): st_write(bs.content, "Description 1")
            with g.cell(): st_write(bs.content, "Description 2")

    # Liens et références
    with st_block(s.center_txt + s.Large):
        st_write(bs.link_style, "Lien 1", link="[https://example1.com](https://example1.com)")
        st_space(size=1)
        st_write(bs.link_style, "Lien 2", link="[https://example2.com](https://example2.com)")

    return html

```

## 🧩 Blocs Composites (Sous-blocs atomiques)

```python
# Bloc composite : charge des sous-blocs depuis le dossier _atomic/
import streamtex as stx
from streamtex import st_include

bck_text_basics = stx.load_atomic_block("bck_text_basics", __file__)
bck_text_styles = stx.load_atomic_block("bck_text_styles", __file__)

class BlockStyles:
    pass

def build():
    st_include(bck_text_basics)
    st_include(bck_text_styles)
```

- `load_atomic_block(name, __file__)` charge `_atomic/{name}.py` relatif à l'appelant
- Lève `BlockNotFoundError` / `BlockImportError` en cas d'erreur

## 📌 Notes Importantes

1. Utilisez des classes de style pour organiser le code.
2. Combinez les styles avec l'opérateur `+`.
3. Utilisez `st_space()` pour gérer l'espacement.
4. Gardez une hiérarchie de titres appropriée pour la table des matières.

## 🔍 Conseils et Bonnes Pratiques

1. Regroupez les styles communs dans une classe `BlockStyles`.
2. Utilisez des variables pour les styles réutilisables.
3. Commentez les sections complexes.
4. Structurez le code en sections logiques.
5. Utilisez l'espacement vertical pour améliorer la lisibilité.
