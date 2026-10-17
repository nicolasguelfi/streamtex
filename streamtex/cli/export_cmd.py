"""stx export html — generate static HTML from a StreamTeX project (headless)."""

import os
import sys
import time
from pathlib import Path

import click

from .console import get_console

# Streamlit dark-theme defaults (matching streamlit/config.py)
_DARK_DEFAULTS = {
    "backgroundColor": "#0e1117",
    "textColor": "#fafafa",
    "primaryColor": "#ff4b4b",
}
_LIGHT_DEFAULTS = {
    "backgroundColor": "#ffffff",
    "textColor": "#31333f",
    "primaryColor": "#ff4b4b",
}


def _read_streamlit_theme(project_dir: str) -> dict[str, str]:
    """Read theme colors from ``.streamlit/config.toml`` in the project.

    Returns a dict with keys ``bg``, ``text``, ``primary`` (any may be empty).
    Resolves ``base = "dark"`` into concrete color values when individual
    colors are not set.
    """
    config_path = os.path.join(project_dir, ".streamlit", "config.toml")
    if not os.path.isfile(config_path):
        return {}

    try:
        import tomllib
    except ModuleNotFoundError:
        try:
            import tomli as tomllib  # type: ignore[no-redef]
        except ModuleNotFoundError:
            return {}

    try:
        with open(config_path, "rb") as f:
            cfg = tomllib.load(f)
    except Exception:
        return {}

    theme = cfg.get("theme", {})
    if not theme:
        return {}

    base = theme.get("base", "")
    defaults = _DARK_DEFAULTS if base == "dark" else _LIGHT_DEFAULTS if base == "light" else {}

    return {
        "bg": theme.get("backgroundColor", defaults.get("backgroundColor", "")),
        "text": theme.get("textColor", defaults.get("textColor", "")),
        "primary": theme.get("primaryColor", defaults.get("primaryColor", "")),
    }


#: Environment variable read when ``--lang`` is not given. It is the same
#: variable a ``book.py`` typically reads to choose the language of its blocks
#: (``st_book(block_kwargs={"lang": os.environ.get("STX_LANG", "en")})``), so a
#: single ``STX_LANG=fr`` drives both the content and the ``<html lang>``.
LANG_ENV_VAR = "STX_LANG"


def resolve_export_lang(lang_option: str | None) -> str:
    """Resolve the export language: ``--lang`` > ``$STX_LANG`` > ``"en"``."""
    if lang_option:
        return lang_option.strip()
    env = os.environ.get(LANG_ENV_VAR, "").strip()
    return env or "en"


@click.command("html")
@click.argument("path", default=".", type=click.Path(exists=True))
@click.option("--output", "-o", default="./static-html",
              help="Output directory for the generated HTML.")
@click.option("--asset-mode", type=click.Choice(["embedded", "external"]),
              default="external",
              help="Asset storage: 'embedded' (base64 inline) or 'external' (data/ folder).")
@click.option("--title", default=None,
              help="Title for the HTML document (defaults to auto-detected book title).")
@click.option("--no-nav", is_flag=True, default=False,
              help="Skip navigation enrichment (no sidebar, marker bar, or search).")
@click.option("--theme", "theme_mode", type=click.Choice(["auto", "dark", "light"]),
              default="auto",
              help="Theme for the export: 'auto' reads .streamlit/config.toml, 'dark'/'light' forces a preset.")
@click.option("--theme-bg", default=None, help="Override background color (e.g. '#0e1117').")
@click.option("--theme-text", default=None, help="Override text color (e.g. '#fafafa').")
@click.option("--lang", default=None,
              help="Language tag for the <html lang> attribute (e.g. 'fr'). "
                   "Defaults to $STX_LANG, then 'en'.")
@click.option("--suffix", default="",
              help="Suffix appended to the output basename (e.g. '-fr' gives "
                   "<project>-fr.html) so one directory can hold several languages.")
@click.option("--html-mode", type=click.Choice(["continuous", "paginated", "both"]),
              default=None,
              help="continuous (one file), paginated (one file per page of the page map) "
                   "or both. Defaults to st_book(html_export_mode=…) of the module.")
def export_html(path, output, asset_mode, title, no_nav, theme_mode, theme_bg, theme_text,
                lang, suffix, html_mode):
    """Generate static HTML from a StreamTeX project without a Streamlit server.

    Exports a fully navigable HTML document with sidebar TOC, floating
    marker navigation bar, and client-side search.  Use --no-nav for
    a raw content-only export.

    \b
    Examples:
        stx export html .
        stx export html --output /app/static-html/ ./manuals/stx_manual_intro
        stx export html --asset-mode embedded .
        stx export html --no-nav .
        STX_LANG=fr stx export html --suffix -fr .     # <html lang="fr">, deck-fr.html
        stx export html --lang fr --output ./out/fr .
        stx export html --html-mode both .              # continuous + one file per page
    """
    from ..export import AssetCollector, AssetMode, ExportConfig

    resolved_lang = resolve_export_lang(lang)

    console = get_console()
    project_dir = os.path.abspath(path)
    book_py = os.path.join(project_dir, "book.py")

    if not os.path.isfile(book_py):
        console.print(f"[red]Error:[/] {book_py} not found.")
        raise SystemExit(1)

    console.print(f"[bold]HTML export[/] for [cyan]{project_dir}[/]")

    # Resolve theme colors BEFORE entering headless context
    # Priority: --theme-bg/--theme-text > --theme dark/light > .streamlit/config.toml > defaults
    resolved_bg = theme_bg
    resolved_text = theme_text
    resolved_primary = None

    if not resolved_bg or not resolved_text:
        if theme_mode == "dark":
            resolved_bg = resolved_bg or _DARK_DEFAULTS["backgroundColor"]
            resolved_text = resolved_text or _DARK_DEFAULTS["textColor"]
            resolved_primary = _DARK_DEFAULTS["primaryColor"]
        elif theme_mode == "light":
            resolved_bg = resolved_bg or _LIGHT_DEFAULTS["backgroundColor"]
            resolved_text = resolved_text or _LIGHT_DEFAULTS["textColor"]
            resolved_primary = _LIGHT_DEFAULTS["primaryColor"]
        else:
            # auto: read from .streamlit/config.toml
            detected = _read_streamlit_theme(project_dir)
            if detected:
                resolved_bg = resolved_bg or detected.get("bg") or None
                resolved_text = resolved_text or detected.get("text") or None
                resolved_primary = detected.get("primary") or None
                if detected.get("bg"):
                    console.print("[green]\u2713 Theme:[/] detected from .streamlit/config.toml")

    # Build the ExportConfig that will be injected into warmup mode
    use_external = asset_mode == "external"
    export_cfg = ExportConfig(
        enabled=True,
        page_title=title or "StreamTeX Export",
        asset_mode=AssetMode.EXTERNAL if use_external else AssetMode.EMBEDDED,
        theme_bg=resolved_bg,
        theme_text=resolved_text,
        theme_primary=resolved_primary,
        lang=resolved_lang,
    )
    console.print(f"[green]\u2713 Language:[/] <html lang=\"{resolved_lang}\">")

    # Add project dir to sys.path so ``import setup`` / ``import blocks`` work.
    if project_dir not in sys.path:
        sys.path.insert(0, project_dir)

    # Save and restore cwd (book.py may change it).
    original_cwd = os.getcwd()
    os.chdir(project_dir)

    full_html = None
    nav_data = None

    # Reuse the headless Streamlit mock from cache_cmd
    from .cache_cmd import _headless_streamlit

    with _headless_streamlit():
        # Enable warmup mode + export in streamtex.book
        from streamtex import book as _book_mod
        _book_mod._warmup_mode = True
        _book_mod._warmup_export_config = export_cfg
        _book_mod._export_page_sentinels = True        # where pages start (#106)
        _book_mod._html_export_mode = "continuous"

        t0 = time.time()
        try:
            code = Path(book_py).read_text(encoding="utf-8")
            exec(compile(code, book_py, "exec"),  # noqa: S102
                 {"__name__": "__main__", "__file__": book_py})
        except SystemExit:
            pass  # st.set_page_config may call sys.exit in some edge cases
        except Exception as e:
            from streamtex.book import IncludeCycleError
            if not isinstance(e, IncludeCycleError):
                raise
            # a block includes itself: nothing is written (#119)
            console.print(f"[red]Error:[/] {e}")
            raise SystemExit(1) from None
        finally:
            _book_mod._warmup_mode = False
            _book_mod._warmup_export_config = None
            _book_mod._export_page_sentinels = False
            os.chdir(original_cwd)

        # Retrieve the captured HTML and nav data while session_state is the mock dict
        import streamlit as st
        full_html = st.session_state.get(_book_mod._STX_FULL_EXPORT_HTML_KEY)
        nav_data = st.session_state.get("_stx_export_nav")
        _cache_data = st.session_state.get(_book_mod._STX_CACHE_KEY) or {}

    elapsed = time.time() - t0

    if not full_html:
        console.print(
            f"[yellow]Warning:[/] export completed in {elapsed:.1f}s "
            f"but no HTML was captured. "
            f"Is export=True set in st_book()?"
        )
        raise SystemExit(1)

    from ..export import strip_page_sentinels
    from ..export_paginate import build_entry_html, build_page_documents, to_subfolder

    mode = html_mode or _book_mod._html_export_mode
    raw_html = full_html
    full_html = strip_page_sentinels(raw_html)           # the continuous document

    # Derive the base name from the project directory
    base_name = os.path.basename(project_dir).replace("stx_manual_", "") + suffix
    output_dir = os.path.abspath(output)
    nav_toc = (nav_data or {}).get("toc") or []
    nav_markers = (nav_data or {}).get("markers") or []

    # The paginated files (#106): one per page of the module's page map
    paged = None
    if mode in ("paginated", "both"):
        pages = _cache_data.get("pages") or []
        paged = build_page_documents(raw_html, pages, nav_toc) if pages else None
        if paged is None:
            console.print("[red]Error:[/] no page map in the page cache: cannot paginate.")
            raise SystemExit(1)
    pages_dir_name = "pages" if use_external else f"{base_name}-pages"

    from ..export import lazy_load_images

    def _enrich(html_in, page_nav=None):
        html_in = lazy_load_images(html_in, nav_markers)       # each output file (#115)
        if no_nav or not nav_data:
            return html_in
        from ..export_enrich import enrich_export_html
        return enrich_export_html(
            html_in,
            toc=nav_toc,
            markers=nav_markers,
            search_index=nav_data.get("search_index"),
            doc_version=_cache_data.get("doc_version", ""),
            lib_version=_cache_data.get("lib_version", ""),
            page_nav=page_nav,
        )

    if not no_nav and nav_data:
        features = []
        if nav_data.get("toc"):
            features.append("TOC sidebar")
        if nav_data.get("markers"):
            features.append("marker nav")
        if nav_data.get("search_index"):
            features.append("search")
        if features:
            console.print(f"[green]\u2713 Navigation:[/] {', '.join(features)}")

    # Materialise served media (configure_image_path) so the export is
    # self-contained — headless: resolve against the project dir (#48).
    from ..export import materialize_served_media

    def _materialize(html_in, coll):
        # configure_image_path may use a RELATIVE fs_root — resolve it
        # against the project dir, not the caller's cwd.
        cwd = os.getcwd()
        os.chdir(project_dir)
        try:
            return materialize_served_media(html_in, coll,
                                            project_root=project_dir)
        finally:
            os.chdir(cwd)

    collector = AssetCollector() if use_external else None
    folder = Path(output_dir) / base_name if use_external else Path(output_dir)
    continuous_name = f"{base_name}.html"

    # Page files first: they register their assets in the shared collector
    if paged is not None:
        files_by_page, docs = paged
        pages_dir = folder / pages_dir_name
        pages_dir.mkdir(parents=True, exist_ok=True)
        other = f"../{continuous_name}" if mode == "both" else None
        for fname, doc, here in docs:
            doc = _enrich(doc, {"mode": "paginated", "files": files_by_page, "here": here,
                                "prefix": "", "other": other})
            doc = _materialize(doc, collector)
            if collector is not None:
                doc = to_subfolder(collector.rewrite_html(doc))
            (pages_dir / fname).write_text(doc, encoding="utf-8")
        console.print(f"[green]\u2713 Paginated:[/] {len(docs)} page file(s) in [cyan]{pages_dir}[/]")

    if mode == "paginated":
        # the entry file keeps today's address and sends every link to its page
        folder.mkdir(parents=True, exist_ok=True)
        entry = build_entry_html(paged[0], f"{pages_dir_name}/", nav_markers, nav_toc,
                                 title or export_cfg.page_title, export_cfg.lang)
        html_path = folder / continuous_name
        html_path.write_text(entry, encoding="utf-8")
        if collector is not None:
            for asset in collector.assets.values():
                target = folder / asset.relative_path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(asset.data)
        console.print(f"[green]Done[/] in {elapsed:.1f}s — entry file [cyan]{html_path}[/]")
        return

    page_nav = ({"mode": "continuous", "files": paged[0], "here": None,
                 "prefix": f"{pages_dir_name}/", "other": f"{pages_dir_name}/"}
                if paged is not None else None)
    full_html = _enrich(full_html, page_nav)

    # Write to disk — the collector extracts data URIs (the global one was
    # reset by _build_page_cache after capturing HTML)
    if use_external:
        full_html = _materialize(full_html, collector)
        html_path = collector.write_to_disk(full_html, output_dir, base_name)
        asset_count = len(collector.assets)
        console.print(
            f"[green]Done[/] in {elapsed:.1f}s — "
            f"HTML + {asset_count} asset(s) written to [cyan]{html_path}[/]"
        )
    else:
        # Embedded mode: single HTML file with base64 data URIs intact
        full_html = _materialize(full_html, None)
        out_dir = Path(output_dir)
        out_dir.mkdir(parents=True, exist_ok=True)
        html_path = out_dir / continuous_name
        html_path.write_text(full_html, encoding="utf-8")
        console.print(
            f"[green]Done[/] in {elapsed:.1f}s — "
            f"HTML written to [cyan]{html_path}[/]"
        )
