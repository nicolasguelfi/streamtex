"""Browser detection banner — recommends Chrome for best performance."""

from .export import _render

_CHROME_BANNER_JS = """\
<script>
(function() {
  // Only run in top-level Streamlit context
  var win = window.parent || window;
  var doc = win.document;
  if (doc.getElementById('stx-chrome-banner')) return;

  var isChrome = /Chrome\\//.test(navigator.userAgent)
                 && !/Edg\\//.test(navigator.userAgent)
                 && !/OPR\\//.test(navigator.userAgent);
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

    Called automatically by ``st_book()`` (``chrome_banner=True`` by default).
    Can also be called manually in ``book.py``.
    """
    _render(_CHROME_BANNER_JS)
