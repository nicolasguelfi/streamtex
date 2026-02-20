import streamlit as st
from dataclasses import dataclass
from .styles import Style, StreamTeX_Styles as s
from .enums import Tag
from typing import Optional

streamtex_toc_items = "_streamtex_toc_items"
streamtex_toc_lvl = "_streamtex_toc_lvl"

@dataclass
class TOCConfig:
    """
    Class representing configuration for the Table of Contents.
    """
    
    numerate_titles: bool = True
    '''A boolean dictating whether to add numering in the ToC titles.'''
    toc_position: int = -1
    '''-1 means at the end, 0 at the start, None means no ToC'''
    title_style: Style = s.text.titles.title
    '''A Style object dictating how the ToC main title should look.'''
    content_style: Style = s.text.titles.subtitle
    '''A Style object dictating how the ToC content (the listing of titles) should look.'''


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
        
        # Generate numbering if numeration is enabled
        section_number = ".".join(map(str, self.numbers)) + " "
        has_num = self.config.numerate_titles
            
        # Create a simple slug
        key_anchor = self.get_key_anchor(section_number + label)
            
        # Add the ToC entry to the list
        self.get_entries().append({
            "level": lvl,
            "title": section_number + label if has_num else label,
            "key_anchor": key_anchor,
            "_reg_label": label,
            "_reg_level": level,
        })
        
        if not self.config.numerate_titles:
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