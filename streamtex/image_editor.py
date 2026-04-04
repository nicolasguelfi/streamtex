"""Image editor panel — editable=True support for st_image().

Renders an expandable panel allowing users to:
- Rename the image (give it a semantic name)
- Replace from local path or URL
- Generate/regenerate via AI (with prompt editing)
- Use current image as base for AI img2img editing
- View version history
"""

from __future__ import annotations

import hashlib
import logging
import os
from typing import Optional

from .styles import Style

logger = logging.getLogger(__name__)

try:
    import streamlit as st
except ImportError:
    st = None


def _stable_key(prefix: str, *parts) -> str:
    """Generate a stable Streamlit widget key from parts."""
    payload = "|".join(str(p) for p in parts)
    h = hashlib.sha256(payload.encode()).hexdigest()[:10]
    return f"{prefix}_{h}"


def _render_editor_panel(
    *,
    uri: str,
    name: str,
    prompt: Optional[str],
    provider: Optional[str],
    model: Optional[str],
    ai_size: Optional[str],
    quality: str,
    style: Style,
    width: str,
    height: str,
    alt: str,
    link: str,
    hover: bool,
    light_bg: bool,
) -> None:
    """Render the image editor panel inside an expander."""
    if st is None:
        return

    # Skip editor during cache build (interactive-only, no TOC/marker/search value)
    from .export import is_cache_building
    if is_cache_building():
        return

    key_base = _stable_key("img_edit", uri, name)
    session_prefix = f"stx_img_editor_{key_base}"

    # st.container(key=) provides a stable DOM anchor for the editor subtree,
    # preventing flickering on reruns.  st.expander and st.tabs do not support
    # key= in Streamlit 1.54 — the keyed container stabilises them instead.
    with st.container(key=f"editor_{key_base}"):
        with st.expander("Edit Image", expanded=False):
            # --- Tab layout: Source | AI Generate | History | Display ---
            tabs = ["Source", "AI Generate", "History", "Display"]
            tab_source, tab_ai, tab_history, tab_display = st.tabs(tabs)

            # ===== SOURCE TAB =====
            with tab_source:
                _render_source_tab(
                    uri=uri, name=name, key_base=key_base,
                    session_prefix=session_prefix,
                    style=style, width=width, height=height,
                    alt=alt, link=link, hover=hover, light_bg=light_bg,
                )

            # ===== AI GENERATE TAB =====
            with tab_ai:
                _render_ai_tab(
                    uri=uri, name=name, prompt=prompt,
                    provider=provider, model=model,
                    ai_size=ai_size, quality=quality,
                    key_base=key_base, session_prefix=session_prefix,
                    style=style, width=width, height=height,
                    alt=alt, link=link, hover=hover, light_bg=light_bg,
                )

            # ===== HISTORY TAB =====
            with tab_history:
                _render_history_tab(
                    name=name, key_base=key_base,
                    session_prefix=session_prefix,
                )

            # ===== DISPLAY TAB =====
            with tab_display:
                _render_display_tab(
                    name=name, width=width, height=height,
                    key_base=key_base,
                )

    # Display settings are applied via session_state in st_image() (step 1c)
    # on the next rerun — no CSS injection needed.


def _render_source_tab(
    *, uri, name, key_base, session_prefix,
    style, width, height, alt, link, hover, light_bg,
):
    """Source tab: rename, replace from path/URL."""
    # Name field
    current_name = name or (os.path.splitext(os.path.basename(uri))[0] if uri else "")
    new_name = st.text_input(
        "Image name",
        value=current_name,
        key=f"{key_base}_name",
        help="Semantic name for version tracking",
    )

    # Current source
    st.caption(f"Current: {uri}")

    # Replace source
    source_type = st.radio(
        "Replace with",
        ["Keep current", "Local path", "URL"],
        key=f"{key_base}_source_type",
        horizontal=True,
    )

    if source_type == "Local path":
        new_path = st.text_input(
            "File path (relative to project root)",
            key=f"{key_base}_new_path",
        )
        if st.button("Apply", key=f"{key_base}_apply_path"):
            if new_path and os.path.isfile(new_path):
                _save_managed_image(
                    image_path=new_path,
                    name=new_name or current_name,
                    source_type="local",
                )
                st.success(f"Saved as managed image: {new_name or current_name}")
                st.rerun()
            else:
                st.error("File not found")

    elif source_type == "URL":
        new_url = st.text_input(
            "Image URL",
            key=f"{key_base}_new_url",
        )
        if st.button("Apply", key=f"{key_base}_apply_url"):
            if new_url:
                downloaded = _download_url_image(new_url)
                if downloaded:
                    _save_managed_image(
                        image_path=downloaded,
                        name=new_name or current_name,
                        source_type="url",
                        original_path=new_url,
                    )
                    st.success(f"Downloaded and saved: {new_name or current_name}")
                    st.rerun()
                else:
                    st.error("Failed to download image")

    # Rename (if name changed)
    if new_name and new_name != current_name and current_name:
        if st.button("Rename", key=f"{key_base}_rename"):
            try:
                from .ai.history import rename_image
                result = rename_image(current_name, new_name)
                if result:
                    st.success(f"Renamed to: {new_name}")
                    st.rerun()
            except FileExistsError as e:
                st.error(str(e))


def _render_ai_tab(
    *, uri, name, prompt, provider, model, ai_size, quality,
    key_base, session_prefix, style, width, height,
    alt, link, hover, light_bg,
):
    """AI Generate tab: prompt editing, provider/model selection, img2img."""
    # Provider selection
    try:
        from .ai.providers import get_available_models, list_providers
    except ImportError:
        st.warning("AI image generation requires `streamtex[ai]`")
        return

    available = list_providers()
    if not available:
        st.warning("No AI providers available. Install `streamtex[ai]`.")
        return

    col1, col2 = st.columns(2)
    with col1:
        default_provider = provider or "openai"
        idx = available.index(default_provider) if default_provider in available else 0
        selected_provider = st.selectbox(
            "Provider",
            available,
            index=idx,
            key=f"{key_base}_ai_provider",
        )

    with col2:
        models = get_available_models(selected_provider)
        default_model = model or (models[0] if models else "")
        model_idx = models.index(default_model) if default_model in models else 0
        selected_model = st.selectbox(
            "Model",
            models if models else ["(default)"],
            index=model_idx if models else 0,
            key=f"{key_base}_ai_model",
        )

    # Size and quality — dynamic from model capabilities
    try:
        from .ai.providers.registry import get_model_capabilities
        caps = get_model_capabilities(
            selected_provider,
            selected_model if selected_model != "(default)" else None,
        )
        sizes = caps.sizes
        qualities = caps.qualities
    except Exception:
        sizes = ["1024x1024", "1024x1536", "1536x1024"]
        qualities = ["standard", "hd"]
        caps = None

    col3, col4 = st.columns(2)
    with col3:
        default_size = ai_size if ai_size in sizes else caps.default_size if caps else sizes[0]
        size_idx = sizes.index(default_size) if default_size in sizes else 0
        selected_size = st.selectbox(
            "Size",
            sizes,
            index=size_idx,
            key=f"{key_base}_ai_size",
        )
    with col4:
        q_default = quality if quality in qualities else (caps.default_quality if caps else qualities[0])
        q_idx = qualities.index(q_default) if q_default in qualities else 0
        selected_quality = st.selectbox(
            "Quality",
            qualities,
            index=q_idx,
            key=f"{key_base}_ai_quality",
        )

    # Prompt
    current_prompt = prompt or ""
    user_prompt = st.text_area(
        "Prompt",
        value=current_prompt,
        height=120,
        key=f"{key_base}_ai_prompt",
    )

    # Image-to-image option
    use_base = False
    if uri and os.path.isfile(uri):
        use_base = st.checkbox(
            "Use current image as base (image-to-image editing)",
            key=f"{key_base}_use_base",
        )

    # Generate button
    if st.button("Generate", key=f"{key_base}_ai_generate", type="primary"):
        if not user_prompt.strip():
            st.error("Please enter a prompt")
            return

        with st.spinner("Generating image..."):
            try:
                from .ai.config import AIImageConfig, get_ai_image_config
                from .ai.generate import generate_image

                cfg = get_ai_image_config() or AIImageConfig()

                # Load base image bytes if img2img
                base_bytes = None
                if use_base and uri and os.path.isfile(uri):
                    with open(uri, "rb") as f:
                        base_bytes = f.read()

                file_path = generate_image(
                    user_prompt.strip(),
                    provider=selected_provider,
                    size=selected_size,
                    quality=selected_quality,
                    model=selected_model if selected_model != "(default)" else None,
                    config=cfg,
                    base_image=base_bytes,
                )

                # Save as managed version
                img_name = name or (os.path.splitext(os.path.basename(uri))[0] if uri else "ai_image")
                _save_managed_image(
                    image_path=file_path,
                    name=img_name,
                    source_type="ai_generated",
                    prompt=user_prompt.strip(),
                    provider=selected_provider,
                    model=selected_model if selected_model != "(default)" else None,
                    size=selected_size,
                    quality=selected_quality,
                    base_image=uri if use_base else None,
                )
                st.success(f"Generated and saved: {img_name}")
                st.rerun()

            except Exception as e:
                st.error(f"Generation failed: {e}")


def _render_history_tab(*, name, key_base, session_prefix):
    """History tab: show versions, allow rollback."""
    if not name:
        st.caption("Set an image name to enable version tracking.")
        return

    try:
        from .ai.history import list_versions, rollback
    except ImportError:
        st.caption("History module not available.")
        return

    versions = list_versions(name)
    if not versions:
        st.caption("No version history yet.")
        return

    st.caption(f"{len(versions)} version(s)")
    for ver_num, meta in reversed(versions):
        is_current = ver_num == versions[-1][0]
        label = f"v{ver_num}" + (" (current)" if is_current else "")

        with st.container(border=True):
            cols = st.columns([1, 3, 1])
            with cols[0]:
                st.markdown(f"**{label}**")
            with cols[1]:
                source = meta.source_type
                if meta.prompt:
                    st.caption(f"{source} | {meta.provider or '?'} | {meta.prompt[:80]}...")
                else:
                    st.caption(f"{source} | {meta.original_path or 'unknown'}")
                st.caption(f"{meta.timestamp[:19]}")
            with cols[2]:
                if not is_current:
                    if st.button("Restore", key=f"{key_base}_restore_{ver_num}"):
                        result = rollback(name, ver_num)
                        if result:
                            st.success(f"Restored v{ver_num}")
                            st.rerun()


# ---------------------------------------------------------------------------
# Display tab
# ---------------------------------------------------------------------------


def _load_display_from_metadata(name: str, prefix: str) -> None:
    """Load persisted display settings from metadata JSON into session_state.

    Called once per session — if session_state already has values, skip.
    """
    init_key = f"{prefix}_initialized"
    if st.session_state.get(init_key):
        return
    st.session_state[init_key] = True

    try:
        from .ai.history import get_current_metadata
        meta = get_current_metadata(name)
        if meta:
            if meta.display_zoom is not None:
                st.session_state.setdefault(f"{prefix}_zoom", meta.display_zoom)
            if meta.display_width is not None:
                st.session_state.setdefault(f"{prefix}_width", meta.display_width)
            if meta.display_height is not None:
                st.session_state.setdefault(f"{prefix}_height", meta.display_height)
            if meta.display_keep_ratio is not None:
                st.session_state.setdefault(f"{prefix}_keep_ratio", meta.display_keep_ratio)
    except Exception:
        logger.debug("Failed to load display settings from metadata", exc_info=True)


def _persist_display_to_metadata(name: str, prefix: str) -> None:
    """Save current display settings to the metadata JSON."""
    try:
        from .ai.history import get_current, get_current_metadata
        from .ai.metadata import metadata_path_for, save_metadata

        current = get_current(name)
        if not current:
            return
        meta = get_current_metadata(name)
        if not meta:
            return

        meta.display_zoom = st.session_state.get(f"{prefix}_zoom")
        meta.display_width = st.session_state.get(f"{prefix}_width") or None
        meta.display_height = st.session_state.get(f"{prefix}_height") or None
        meta.display_keep_ratio = st.session_state.get(f"{prefix}_keep_ratio", True)
        save_metadata(meta, metadata_path_for(current))
    except Exception:
        logger.debug("Failed to persist display settings to metadata", exc_info=True)


def _render_display_tab(*, name, width, height, key_base):
    """Display tab: two exclusive modes — Zoom (default) or Custom size."""
    if not name:
        st.caption("Set an image name to enable display adjustments.")
        return

    prefix = f"stx_img_display_{name}"

    # Load persisted values on first run
    _load_display_from_metadata(name, prefix)

    # Determine initial mode from persisted state
    has_custom = bool(
        st.session_state.get(f"{prefix}_width")
        or st.session_state.get(f"{prefix}_height")
    )
    default_mode = "Custom size" if has_custom else "Zoom"

    # Snapshot for change detection
    prev_zoom = st.session_state.get(f"{prefix}_zoom", 100)
    prev_w = st.session_state.get(f"{prefix}_width", "")
    prev_h = st.session_state.get(f"{prefix}_height", "")

    # --- Mode selector ---
    mode = st.radio(
        "Sizing mode",
        ["Zoom", "Custom size"],
        index=0 if default_mode == "Zoom" else 1,
        key=f"{key_base}_display_mode",
        horizontal=True,
        label_visibility="collapsed",
    )

    changed = False

    if mode == "Zoom":
        # Transfer custom width % to zoom when switching back
        if prev_w:
            if prev_w.strip().endswith("%"):
                try:
                    pct = int(prev_w.strip().rstrip("%"))
                    if 10 <= pct <= 200:
                        st.session_state[f"{prefix}_zoom"] = pct
                        prev_zoom = pct
                except ValueError:
                    logger.debug("Failed to parse zoom percentage from width value", exc_info=True)
            st.session_state[f"{prefix}_width"] = ""
            st.session_state[f"{prefix}_height"] = ""
            changed = True
        elif prev_h:
            st.session_state[f"{prefix}_height"] = ""
            changed = True

        zoom = st.slider(
            "Zoom (%)",
            min_value=10, max_value=200,
            value=int(prev_zoom),
            step=5,
            key=f"{key_base}_display_zoom",
        )
        st.session_state[f"{prefix}_zoom"] = zoom

        if zoom != prev_zoom:
            changed = True

        if st.button("Reset to 100%", key=f"{key_base}_display_reset"):
            st.session_state[f"{prefix}_zoom"] = 100
            changed = True

    else:
        # Custom size mode — transfer zoom value to width, then reset zoom
        if prev_zoom != 100 and not prev_w:
            st.session_state[f"{prefix}_width"] = f"{prev_zoom}%"
            prev_w = f"{prev_zoom}%"
            st.session_state[f"{prefix}_zoom"] = 100
            changed = True
        elif prev_zoom != 100:
            st.session_state[f"{prefix}_zoom"] = 100
            changed = True

        keep_ratio = st.checkbox(
            "Keep proportions",
            value=st.session_state.get(f"{prefix}_keep_ratio", True),
            key=f"{key_base}_display_keep_ratio",
        )
        st.session_state[f"{prefix}_keep_ratio"] = keep_ratio

        col1, col2 = st.columns(2)
        with col1:
            new_w = st.text_input(
                "Width",
                value=prev_w,
                key=f"{key_base}_display_width",
                placeholder="e.g. 80%, 400px, 50vw",
            )
            st.session_state[f"{prefix}_width"] = new_w
        with col2:
            new_h = st.text_input(
                "Height",
                value=prev_h,
                key=f"{key_base}_display_height",
                placeholder="e.g. auto, 300px, 40vh",
            )
            st.session_state[f"{prefix}_height"] = new_h

        if new_w != prev_w or new_h != prev_h:
            changed = True

        if st.button("Reset", key=f"{key_base}_display_reset"):
            st.session_state[f"{prefix}_width"] = ""
            st.session_state[f"{prefix}_height"] = ""
            st.session_state[f"{prefix}_keep_ratio"] = True
            changed = True

    # Persist + rerun when values changed
    if changed:
        _persist_display_to_metadata(name, prefix)
        st.rerun()


# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------

def _save_managed_image(
    image_path: str,
    name: str,
    source_type: str = "local",
    **kwargs,
) -> str:
    """Save an image as a managed versioned image."""
    from .ai.history import save_version
    return save_version(
        name=name,
        image_path=image_path,
        source_type=source_type,
        **kwargs,
    )


def _download_url_image(url: str) -> Optional[str]:
    """Download an image from URL to a temp file. Returns path or None."""
    try:
        import tempfile

        import requests
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()

        # Detect extension from content-type
        ct = resp.headers.get("content-type", "image/png")
        ext = "png"
        if "jpeg" in ct or "jpg" in ct:
            ext = "jpeg"
        elif "webp" in ct:
            ext = "webp"
        elif "svg" in ct:
            ext = "svg"

        fd, path = tempfile.mkstemp(suffix=f".{ext}")
        with os.fdopen(fd, "wb") as f:
            f.write(resp.content)
        return path
    except Exception:
        return None
