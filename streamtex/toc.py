from dataclasses import dataclass
from typing import Optional

from .styles import StxStyles as s
from .styles import Style

streamtex_toc_items = "_streamtex_toc_items"
streamtex_toc_lvl = "_streamtex_toc_lvl"


class NumberingMode:
    """Where hierarchical numbering prefixes appear."""
    NONE = "none"
    BOTH = "both"
    SIDEBAR_ONLY = "sidebar"
    MAIN_ONLY = "main"


@dataclass
class TOCConfig:
    """
    Class representing configuration for the Table of Contents.
    """

    numbering: str = NumberingMode.BOTH
    '''NumberingMode value controlling where numbering appears
    (sidebar/main/both/none).'''
    toc_position: int = -1
    '''-1 means at the end, 0 at the start, None means no ToC'''
    title_style: Style = s.text.titles.title
    '''A Style object dictating how the ToC main title should look.'''
    content_style: Style = s.text.titles.subtitle
    '''A Style object dictating how the ToC content (the listing of titles) should look.'''
    search: bool = False
    '''Enable full-text search filtering in the TOC sidebar.'''
    search_placeholder: str = "Search..."
    '''Placeholder text for the search input field.'''
    sidebar_max_level: int | None = None
    '''Max TOC hierarchy level shown in sidebar.
    None = mode-dependent default (paginated: 1, continuous: 2).'''

    @property
    def effective_numbering(self) -> str:
        """Return the active numbering mode."""
        return self.numbering


class TOCRegistry:
    '''A class to register ToC levels.'''
    def __init__(self, config: TOCConfig = TOCConfig()):
        self.config = config
        '''Configuration for the ToC.'''
        self.toc_list = []
        '''A list of ToC levels registered.'''
        self.current_level = 1
        '''The starting level of the ToC. It is used to keep track of the ToC during generation.'''
        self.numbers = []
        '''List to keep track of title numbers.'''

    def get_entries(self):
        '''A list of ToC levels registered.'''
        return self.toc_list

    def reset(self):
        '''Resets the ToC registry.'''
        self.toc_list = []
        self.current_level = 1
        self.numbers = []

    def register_entry(self, label: str, level: str):
        """
        Registers an entry and returns a unique ID (slug) for the anchor.

        `level` can be '+x' or '-x' for relative TOC levels, or just 'x' for absolute TOC levels.
        """
        # Determine the level
        if level.startswith("+") or level.startswith("-"):
            lvl = self.current_level + int(level)
            lvl = max(lvl, 1)
        else:
            lvl = int(level)
            lvl = max(lvl, 1)
            self.current_level = lvl

        # Update section numbering
        while len(self.numbers) < lvl:
            self.numbers.append(0)  # Extend numbering hierarchy
        self.numbers = self.numbers[:lvl]  # Trim unused levels
        self.numbers[-1] += 1  # Increment the current level number

        # Reset numbering for subsequent levels when jumping back in hierarchy
        if len(self.numbers) > lvl:
            self.numbers = self.numbers[:lvl]

        # Generate numbering prefix
        section_number = ".".join(map(str, self.numbers)) + " "

        # Determine where numbering should appear
        mode = self.config.effective_numbering
        sidebar_needs_num = mode in (NumberingMode.BOTH, NumberingMode.SIDEBAR_ONLY)
        main_needs_num = mode in (NumberingMode.BOTH, NumberingMode.MAIN_ONLY)

        # Create a simple slug (always includes the number for stable anchors)
        key_anchor = self.get_key_anchor(section_number + label)

        # Add the ToC entry to the list
        self.get_entries().append({
            "level": lvl,
            "title": section_number + label if sidebar_needs_num else label,
            "section_number": section_number,
            "key_anchor": key_anchor,
            "_reg_label": label,
            "_reg_level": level,
        })

        if not main_needs_num:
            section_number = ""

        return key_anchor, section_number, lvl

    @staticmethod
    def get_key_anchor(title: str):
        import re
        # Replace dots and common punctuation with hyphens
        slug = re.sub(r'[.\'"!?@#$%^&*()+=\[\]{}|\\/<>,;:~`]', '-', title.lower())
        # Collapse whitespace and hyphens into single hyphens
        slug = re.sub(r'[-\s]+', '-', slug).strip('-')
        return slug or 'section'

toc: Optional[TOCRegistry] = None
'''The global ToC Registry.'''


def reset_toc_registry(toc_config: TOCConfig = TOCConfig()):
    """Clears the registry for the current run."""
    global toc
    if toc is not None:
        toc.reset()
    elif toc_config is not None:
        toc = TOCRegistry(toc_config)

def register_toc_entry(label: str, level: str) -> str:
    """
    Registers an entry and returns a unique ID (slug) for the anchor.

    `level` can be '+x' or '-x' for relative TOC levels, or just 'x' for absolute TOC levels.
    """
    global toc
    assert isinstance(toc, TOCRegistry), "TOC Registry is not initialized. Please call reset_toc_registry first."

    return toc.register_entry(label, level)

def toc_entries():
    '''Returns the list of ToC entries registered.'''
    global toc
    assert isinstance(toc, TOCRegistry), "TOC Registry is not initialized. Please call reset_toc_registry first."

    return toc.get_entries()

def get_key_anchor(title: str):
    '''Returns a key anchor version of the title text.'''
    return TOCRegistry.get_key_anchor(title)
