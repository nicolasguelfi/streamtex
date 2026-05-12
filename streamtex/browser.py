"""Browser detection banner — historical helper, off by default since 0.6.25.

The banner was introduced when streamtex rendered every construct through
CSS ``:has()`` selectors, which triggered a 3-4 s freeze on Chrome cold
load and were not supported at all in Firefox until v121 (2023-12).  The
marker-runtime migration (0.6.11 → 0.6.16) eliminated both issues:
``:has()`` is no longer used, and the new MutationObserver-based path is
universally supported.

The only remaining Chrome-specific edge is the non-standard ``zoom`` CSS
property used by ``st_zoom``, which Firefox added in v126 (2024-05).  At
this point Chrome no longer offers a meaningful advantage for streamtex
content, so the banner is off by default in ``st_book(chrome_banner=…)``.
The function remains exported for users who still want to opt back in.
"""

import streamlit as st

_CHROME_BANNER_JS = """\
<script>
(function() {
  // Only run in top-level Streamlit context
  var win = window.parent || window;
  var doc = win.document;
  if (doc.getElementById('stx-chrome-banner')) return;

  var ua = navigator.userAgent;
  // All iOS browsers use WebKit — no Chrome advantage, skip banner entirely
  var isIOS = /iPad|iPhone|iPod/.test(ua)
              || (navigator.platform === 'MacIntel' && navigator.maxTouchPoints > 1);
  if (isIOS) return;

  var isChrome = (/Chrome\\//.test(ua) || /CriOS\\//.test(ua))
                 && !/Edg\\//.test(ua)
                 && !/OPR\\//.test(ua);
  if (isChrome) return;

  var banner = doc.createElement('div');
  banner.id = 'stx-chrome-banner';
  banner.innerHTML =
    '<span style="margin-right:6px">&#9432;</span>' +
    'For the best experience, use ' +
    '<a href="https://www.google.com/chrome/" target="_blank" rel="noopener" ' +
    'style="color:white;text-decoration:underline;font-weight:700">Google Chrome</a>.' +
    '<span style="margin-left:12px;cursor:pointer;opacity:0.8" ' +
    'onclick="this.parentElement.remove()">&#10005;</span>';
  banner.style.cssText =
    'position:fixed; top:0; left:0; right:0; z-index:999999; ' +
    'background:linear-gradient(90deg,#4285F4 0%,#34A853 100%); ' +
    'color:white; text-align:center; padding:8px 16px; ' +
    'font-family:sans-serif; font-size:14px; font-weight:500;';
  doc.body.insertBefore(banner, doc.body.firstChild);
})();
</script>
"""


def st_chrome_banner() -> None:
    """Show a dismissible banner recommending Chrome if the browser is not Chrome.

    Injects a fixed-position banner into the parent Streamlit frame.
    Does not create a Streamlit component in the block flow, so it
    won't interfere with block numbering or the TOC.

    Disabled by default in ``st_book(chrome_banner=False)`` since 0.6.25
    — the marker-runtime migration removed the original Chrome-specific
    advantage.  Call this manually in ``book.py`` if you still want the
    banner, or pass ``chrome_banner=True`` to ``st_book``.
    """
    st.iframe(_CHROME_BANNER_JS, height=1)
