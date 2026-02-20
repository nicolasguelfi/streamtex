"""Collection system for organizing multiple StreamTeX projects."""

import os
import tomllib
from dataclasses import dataclass, field
from typing import Dict, Optional

import streamlit as st

from .styles import Style, StxStyles
from .write import st_write
from .image import st_image
from .grid import st_grid
from .export import _render


@dataclass
class ProjectMeta:
    """Metadata for a single project in a collection."""

    title: str
    description: str = ""
    cover: str = ""
    project_url: str = ""
    order: int = 0


@dataclass
class CollectionConfig:
    """Configuration for a collection of projects."""

    title: str = "StreamTeX Collection"
    description: str = ""
    cards_per_row: int = 3
    projects: Dict[str, ProjectMeta] = field(default_factory=dict)

    @classmethod
    def from_toml(cls, path: str) -> "CollectionConfig":
        """
        Parse a collection.toml file and return a CollectionConfig instance.

        Args:
            path: Path to the collection.toml file (relative or absolute)

        Returns:
            CollectionConfig instance

        Example (collection.toml):
            ```toml
            [collection]
            title = "University Course Library"
            description = "Curated courses for learning"
            cards_per_row = 3

            [projects.project-aiai18h]
            title = "AI & AI 18h"
            description = "An 18-hour course on AI"
            cover = "static/images/covers/project-aiai18h.png"
            project_url = "http://localhost:8502"
            order = 1

            [projects.project-html-example]
            title = "HTML Migration"
            description = "Learn to migrate HTML to StreamTeX"
            cover = "static/images/covers/project-html-example.png"
            project_url = "http://localhost:8503"
            order = 2
            ```
        """
        if not os.path.isabs(path):
            # Resolve relative to current working directory
            path = os.path.abspath(path)

        if not os.path.exists(path):
            raise FileNotFoundError(f"collection.toml not found at {path}")

        with open(path, "rb") as f:
            try:
                data = tomllib.load(f)
            except Exception as e:
                raise ValueError(
                    f"Failed to parse collection TOML at {path}: {e}\n"
                    f"Check TOML syntax at https://toml.io"
                ) from e

        # Parse collection metadata
        collection_data = data.get("collection", {})
        config = cls(
            title=collection_data.get("title", cls.title),
            description=collection_data.get("description", ""),
            cards_per_row=collection_data.get("cards_per_row", 3),
        )

        # Parse projects
        projects_data = data.get("projects", {})
        for project_key, project_data in projects_data.items():
            project = ProjectMeta(
                title=project_data.get("title", ""),
                description=project_data.get("description", ""),
                cover=project_data.get("cover", ""),
                project_url=project_data.get("project_url", ""),
                order=project_data.get("order", 0),
            )
            config.projects[project_key] = project

        # Sort projects by order
        # Stable sort: order first, then key as tiebreaker
        config.projects = dict(
            sorted(
                config.projects.items(),
                key=lambda item: (item[1].order, item[0]),
            )
        )

        return config


def st_collection(
    config: CollectionConfig,
    home_styles: Optional[object] = None,
) -> None:
    """
    Display a collection of StreamTeX projects.

    In external mode (default), clicking a project card opens the project in a new
    browser tab at the specified URL.

    Args:
        config: CollectionConfig instance (can be created from TOML with CollectionConfig.from_toml())
        home_styles: Style object for home page (usually imported as `Styles` from custom/styles.py)

    Example:
        ```python
        import streamlit as st
        from streamtex import st_collection, CollectionConfig
        from custom.styles import Styles as s

        config = CollectionConfig.from_toml("collection.toml")
        st_collection(config=config, home_styles=s)
        ```
    """
    project_key = st.query_params.get("project")

    if project_key:
        # Check if project exists
        if project_key not in config.projects:
            st.error(f"❌ Project '{project_key}' not found in collection")
            if st.button("← Back to Library"):
                st.query_params.clear()
            st.stop()

        # Show project (external mode: open in new tab)
        _show_project_external(config, project_key)
    else:
        # Show collection home
        _show_home(config, home_styles)


def _show_home(
    config: CollectionConfig,
    home_styles: Optional[object] = None,
) -> None:
    """
    Render the collection home page with a grid of project cards.

    Args:
        config: CollectionConfig instance
        home_styles: Style object for home page styling
    """
    # Title and description
    if home_styles:
        try:
            st_write(home_styles.project.titles.main_title, config.title)
        except AttributeError:
            st.title(config.title)

        if config.description:
            try:
                st_write(home_styles.large, config.description)
            except AttributeError:
                st.markdown(config.description)
    else:
        st.title(config.title)
        if config.description:
            st.markdown(config.description)

    st.divider()

    # Create grid of project cards
    with st_grid(cols=config.cards_per_row) if home_styles else st.container():
        for project_key, project in config.projects.items():
            _render_project_card(config, project_key, project)


def _render_project_card(
    config: CollectionConfig,
    project_key: str,
    project: ProjectMeta,
) -> None:
    """
    Render a single project card with cover image, title, and description.

    When clicked (via JavaScript), opens the project in a new tab.

    Args:
        config: Collection config (for base URL)
        project_key: Project identifier
        project: ProjectMeta instance
    """
    # Get the cover image source
    cover_src = ""
    if project.cover:
        try:
            # Use get_image_src if available
            from .image import get_image_src
            cover_src = get_image_src(project.cover)
        except Exception:
            cover_src = project.cover

    # Build the card HTML
    # Use target="_blank" to open in new tab
    card_html = f"""
    <a href="?project={project_key}" target="_blank" style="text-decoration: none; color: inherit;">
        <div style="
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 16px;
            transition: transform 0.2s, box-shadow 0.2s;
            cursor: pointer;
        "
        onmouseover="this.style.transform='scale(1.02)'; this.style.boxShadow='0 4px 12px rgba(0,0,0,0.15)';"
        onmouseout="this.style.transform='scale(1)'; this.style.boxShadow='none';">
            {f'<img src="{cover_src}" alt="{project.title}" style="width: 100%; height: auto; border-radius: 4px; margin-bottom: 12px;">' if cover_src else ''}
            <h3 style="margin: 8px 0; font-size: 1.3rem;">{project.title}</h3>
            <p style="margin: 8px 0; font-size: 0.95rem; color: #666;">{project.description}</p>
        </div>
    </a>
    """

    _render(card_html)


def _show_project_external(config: CollectionConfig, project_key: str) -> None:
    """
    Show a project in external mode (redirect to external URL).

    Args:
        config: Collection config
        project_key: Project identifier
    """
    project = config.projects[project_key]

    if not project.project_url:
        st.error(f"❌ Project '{project_key}' has no project_url configured")
        st.stop()

    # Sidebar with back button
    with st.sidebar:
        base_url = _get_collection_base_url()
        if st.button("🏠 Back to Library", key="back_to_library"):
            # Clear query params and navigate back to home
            st.query_params.clear()
            st.rerun()

        st.divider()

        st.info(
            f"This project opens at: {project.project_url}\n\n"
            f"Make sure the project is running on that port."
        )

    # Redirect to external URL
    st.write(f"Opening **{project.title}**...")
    redirect_html = (
        f'<meta http-equiv="refresh" content="0;url={project.project_url}?collection_url={base_url}">'
        f'<a href="{project.project_url}">Click here if you are not redirected</a>'
    )
    _render(redirect_html)


def _get_collection_base_url() -> str:
    """
    Get the base URL of the collection (without query params).

    Returns:
        Base URL string (e.g., "http://localhost:8501/")
    """
    # Streamlit provides session state that includes the URL
    # For external mode, we just return a safe default
    # (The actual URL is determined by where the collection is running)
    return "/"
