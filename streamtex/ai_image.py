"""StreamTeX AI image rendering — st_ai_image() and st_ai_image_widget().

Provides two modes:
- **Declarative** (st_ai_image): generate and display an image from a prompt
  directly in block code.
- **Interactive** (st_ai_image_widget): display a prompt editor + generate
  button for end-user interaction within a StreamTeX presentation.

Both functions persist generated images to disk and delegate display to
st_image(), ensuring full compatibility with the export pipeline.
"""

from __future__ import annotations

import os
from typing import Optional

from .ai.config import AIImageConfig, get_ai_image_config
from .ai.generate import AIImageError, generate_image, is_cached
from .image import st_image
from .styles import StxStyles, Style

try:
    import streamlit as st
except ImportError:
    st = None


def st_ai_image(
    prompt: str,
    style: Style = StxStyles.none,
    width: str = "100%",
    height: str = "auto",
    *,
    provider: Optional[str] = None,
    size: Optional[str] = None,
    quality: str = "standard",
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    alt: str = "",
    link: str = "",
    hover: bool = True,
    light_bg: bool = False,
    config: Optional[AIImageConfig] = None,
    **kwargs,
) -> Optional[str]:
    """Generate an AI image and display it.

    .. deprecated::
        Use ``st_image(prompt=..., editable=True)`` instead.
        This function is kept for backwards compatibility.

    In **manual mode** (``auto_generate=False``, the default), if the image
    is not yet cached, a placeholder with a "Generate" button is shown.

    In **auto mode** (``auto_generate=True``), the image is generated
    immediately if not cached.

    Args:
        prompt: Text description of the image to generate.
        style: StreamTeX Style for the image display.
        width: CSS width of the displayed image.
        height: CSS height of the displayed image.
        provider: Provider override ("openai", "google", "fal").
        size: Image size override (e.g. "1024x1024").
        quality: Quality level ("standard" or "hd").
        api_key: API key override.
        model: Model identifier override.
        alt: Alt text for the image.
        link: Optional link URL wrapping the image.
        hover: Enable hover effect on link.
        light_bg: Force white background in iframe.
        config: AIImageConfig override.

    Returns:
        Path to the generated image file, or None if not yet generated.
    """
    cfg = config or get_ai_image_config() or AIImageConfig()
    prov_name = provider or cfg.provider
    img_size = size or cfg.default_size

    # Check if image already exists in cache
    already_cached = is_cached(
        prompt, provider=prov_name, size=img_size,
        quality=quality, model=model, config=cfg, **kwargs,
    )

    if already_cached:
        file_path = generate_image(
            prompt, provider=prov_name, size=img_size,
            quality=quality, api_key=api_key, model=model,
            config=cfg, **kwargs,
        )
        st_image(style=style, width=width, height=height,
                 uri=file_path, alt=alt or prompt, link=link,
                 hover=hover, light_bg=light_bg,
                 editable=True, name="", prompt=prompt,
                 provider=prov_name, model=model,
                 ai_size=img_size, quality=quality)
        return file_path

    # Not cached — behaviour depends on auto_generate
    if cfg.auto_generate:
        try:
            file_path = generate_image(
                prompt, provider=prov_name, size=img_size,
                quality=quality, api_key=api_key, model=model,
                config=cfg, **kwargs,
            )
            st_image(style=style, width=width, height=height,
                     uri=file_path, alt=alt or prompt, link=link,
                     hover=hover, light_bg=light_bg,
                     editable=True, name="", prompt=prompt,
                     provider=prov_name, model=model,
                     ai_size=img_size, quality=quality)
            return file_path
        except AIImageError as e:
            if st is not None:
                st.error(f"AI image generation failed: {e}")
            return None

    # Manual mode: show placeholder + generate button
    if st is not None:
        _show_generate_placeholder(
            prompt, style, width, height, prov_name, img_size,
            quality, api_key, model, alt, link, hover, light_bg, cfg, kwargs,
        )
    return None


def _show_generate_placeholder(
    prompt, style, width, height, provider, size,
    quality, api_key, model, alt, link, hover, light_bg, cfg, extra_kwargs,
):
    """Render a placeholder box with prompt preview and a Generate button."""
    # Use a stable key based on prompt to avoid Streamlit duplicate key errors
    import hashlib
    stable_key = hashlib.sha256(prompt.encode()).hexdigest()[:12]

    container = st.container(border=True)
    with container:
        st.caption(f"AI Image ({provider}) — not yet generated")
        st.text(prompt[:200] + ("..." if len(prompt) > 200 else ""))

        if st.button("Generate", key=f"stx_ai_gen_{stable_key}"):
            with st.spinner("Generating image..."):
                try:
                    file_path = generate_image(
                        prompt, provider=provider, size=size,
                        quality=quality, api_key=api_key, model=model,
                        config=cfg, **extra_kwargs,
                    )
                    st_image(style=style, width=width, height=height,
                             uri=file_path, alt=alt or prompt, link=link,
                             hover=hover, light_bg=light_bg)
                except AIImageError as e:
                    st.error(f"Generation failed: {e}")


def st_ai_image_widget(
    style: Style = StxStyles.none,
    width: str = "100%",
    height: str = "auto",
    *,
    provider: Optional[str] = None,
    default_prompt: str = "",
    size: Optional[str] = None,
    quality: str = "standard",
    api_key: Optional[str] = None,
    model: Optional[str] = None,
    alt: str = "",
    light_bg: bool = False,
    config: Optional[AIImageConfig] = None,
    key: str = "stx_ai_widget",
    show_save: bool = True,
    **kwargs,
) -> Optional[str]:
    """Interactive AI image generation widget.

    Displays a text area for the prompt, optional provider selector,
    a "Generate" button, and the result. Optionally includes a "Save"
    button to copy the image to a permanent location.

    Args:
        style: StreamTeX Style for the displayed image.
        width: CSS width of the displayed image.
        height: CSS height of the displayed image.
        provider: Default provider. If None, uses config default.
        default_prompt: Pre-filled prompt text.
        size: Image size (e.g. "1024x1024").
        quality: Quality level ("standard" or "hd").
        api_key: API key override.
        model: Model identifier override.
        alt: Alt text for the generated image.
        light_bg: Force white background.
        config: AIImageConfig override.
        key: Streamlit widget key prefix.
        show_save: Show a "Save to project" button.

    Returns:
        Path to the generated image, or None if not yet generated.
    """
    if st is None:
        return None

    cfg = config or get_ai_image_config() or AIImageConfig()
    prov_name = provider or cfg.provider
    img_size = size or cfg.default_size

    from .ai.providers import list_providers
    available_providers = list_providers()

    container = st.container(border=True)
    with container:
        st.caption("AI Image Generator")

        # Provider selector (if multiple providers have keys configured)
        if len(available_providers) > 1:
            default_idx = available_providers.index(prov_name) if prov_name in available_providers else 0
            selected_provider = st.selectbox(
                "Provider",
                available_providers,
                index=default_idx,
                key=f"{key}_provider",
            )
        else:
            selected_provider = prov_name

        # Prompt input
        user_prompt = st.text_area(
            "Prompt",
            value=default_prompt,
            key=f"{key}_prompt",
            height=100,
        )

        # Generate button
        col1, col2 = st.columns([1, 3])
        with col1:
            generate_clicked = st.button("Generate", key=f"{key}_generate")

        result_path = None

        if generate_clicked and user_prompt.strip():
            with st.spinner("Generating image..."):
                try:
                    result_path = generate_image(
                        user_prompt.strip(),
                        provider=selected_provider,
                        size=img_size,
                        quality=quality,
                        api_key=api_key,
                        model=model,
                        config=cfg,
                        **kwargs,
                    )
                except AIImageError as e:
                    st.error(f"Generation failed: {e}")

        # Display result (check session state for persistence across reruns)
        session_key = f"{key}_last_path"
        if result_path:
            st.session_state[session_key] = result_path
        last_path = st.session_state.get(session_key)

        if last_path and os.path.isfile(last_path):
            st_image(style=style, width=width, height=height,
                     uri=last_path, alt=alt or user_prompt,
                     light_bg=light_bg)

            if show_save:
                save_name = st.text_input(
                    "Save as (filename)",
                    value=os.path.basename(last_path),
                    key=f"{key}_save_name",
                )
                if st.button("Save to static/images/", key=f"{key}_save"):
                    save_dir = os.path.join(os.getcwd(), "static", "images")
                    os.makedirs(save_dir, exist_ok=True)
                    dest = os.path.join(save_dir, save_name)
                    import shutil
                    shutil.copy2(last_path, dest)
                    st.success(f"Saved to {dest}")

        return last_path
