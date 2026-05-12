"""Bibliography hover preview scaffold — JS/CSS injection for citation cards.

Uses st.iframe() for JS injection (st.html() strips <script> tags even
with unsafe_allow_javascript=True in Streamlit 1.52–1.57; see
documentation/maintenance/components.v1_issue/).  Same parent.document
access pattern as marker.py / zoom.py.

The card is interactive: it stays visible when the mouse enters it, allowing
clicks on the Copy and Open buttons.
"""

import streamlit as st


def inject_bib_preview_scaffold():
    """Inject the bibliography hover card and JS event listeners.

    Targets elements with class="stx-cite" and reads their data-bib-*
    attributes to populate the card.

    Card features:
    - Hover preview with title, authors, venue, DOI, abstract
    - Copy button: copies formatted APA reference to clipboard
    - Open button: opens DOI / URL in a new browser tab
    """

    # CSS via st.html() — rendered inline, styles the whole page
    css = """
    <style>
        #stx-bib-card {
            position: fixed;
            z-index: 999998;
            display: none;
            width: 420px;
            max-width: 90vw;
            background: #1a1a2e;
            border-radius: 10px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.35);
            border: 1px solid rgba(100,140,210,0.25);
            font-family: 'Georgia', 'Times New Roman', serif;
            padding: 16px 20px 12px;
            pointer-events: auto;
            opacity: 0;
            transition: opacity 0.2s ease;
            color: #e0e0e0;
        }
        #stx-bib-card.visible { display: block; opacity: 1; }

        .stx-bib-title {
            font-size: 14px;
            font-weight: 600;
            color: #f0f0f0;
            line-height: 1.4;
            margin-bottom: 6px;
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }
        .stx-bib-authors {
            font-size: 12px;
            color: #a0a0c0;
            margin-bottom: 4px;
            overflow: hidden;
            white-space: nowrap;
            text-overflow: ellipsis;
        }
        .stx-bib-venue {
            font-size: 11px;
            font-style: italic;
            color: #8080b0;
            margin-bottom: 4px;
        }
        .stx-bib-doi {
            font-size: 10px;
            color: #6090d0;
        }
        .stx-bib-abstract {
            font-size: 11px;
            color: #b0b0c0;
            margin-top: 8px;
            padding-top: 8px;
            border-top: 1px solid rgba(255,255,255,0.1);
            display: -webkit-box;
            -webkit-line-clamp: 4;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }

        /* --- Action buttons bar --- */
        .stx-bib-actions {
            display: flex;
            gap: 8px;
            margin-top: 10px;
            padding-top: 8px;
            border-top: 1px solid rgba(255,255,255,0.08);
        }
        .stx-bib-btn {
            flex: 1;
            display: inline-flex;
            align-items: center;
            justify-content: center;
            gap: 5px;
            padding: 5px 10px;
            border: 1px solid rgba(100,140,210,0.3);
            border-radius: 6px;
            background: rgba(100,140,210,0.08);
            color: #90b0e0;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            font-size: 11px;
            cursor: pointer;
            transition: background 0.15s, border-color 0.15s;
            text-decoration: none;
            white-space: nowrap;
        }
        .stx-bib-btn:hover {
            background: rgba(100,140,210,0.2);
            border-color: rgba(100,140,210,0.5);
            color: #b0d0ff;
        }
        .stx-bib-btn.copied {
            background: rgba(80,180,120,0.15);
            border-color: rgba(80,180,120,0.4);
            color: #80d0a0;
        }
        .stx-bib-btn svg {
            width: 13px;
            height: 13px;
            fill: currentColor;
            flex-shrink: 0;
        }
        .stx-bib-btn-open { /* shown only when URL available */ }
        .stx-bib-btn-open[data-url=""] { display: none; }

        .stx-cite {
            cursor: help;
            border-bottom: 1px dotted rgba(96, 144, 208, 0.5);
        }
        .stx-cite:hover {
            border-bottom-color: #6090d0;
        }
    </style>
    """
    st.html(css)

    # SVG icons (inline, no external deps)
    ICON_COPY = '<svg viewBox="0 0 16 16"><path d="M0 6.75C0 5.784.784 5 1.75 5h1.5a.75.75 0 010 1.5h-1.5a.25.25 0 00-.25.25v7.5c0 .138.112.25.25.25h7.5a.25.25 0 00.25-.25v-1.5a.75.75 0 011.5 0v1.5A1.75 1.75 0 019.25 16h-7.5A1.75 1.75 0 010 14.25zM5 1.75C5 .784 5.784 0 6.75 0h7.5C15.216 0 16 .784 16 1.75v7.5A1.75 1.75 0 0114.25 11h-7.5A1.75 1.75 0 015 9.25zm1.75-.25a.25.25 0 00-.25.25v7.5c0 .138.112.25.25.25h7.5a.25.25 0 00.25-.25v-7.5a.25.25 0 00-.25-.25z"/></svg>'
    ICON_CHECK = '<svg viewBox="0 0 16 16"><path d="M13.78 4.22a.75.75 0 010 1.06l-7.25 7.25a.75.75 0 01-1.06 0L2.22 9.28a.75.75 0 011.06-1.06L6 10.94l6.72-6.72a.75.75 0 011.06 0z"/></svg>'
    ICON_OPEN = '<svg viewBox="0 0 16 16"><path d="M3.75 2h3.5a.75.75 0 010 1.5h-3.5a.25.25 0 00-.25.25v8.5c0 .138.112.25.25.25h8.5a.25.25 0 00.25-.25v-3.5a.75.75 0 011.5 0v3.5A1.75 1.75 0 0112.25 14h-8.5A1.75 1.75 0 012 12.25v-8.5C2 2.784 2.784 2 3.75 2zm6.5 0h3a.75.75 0 01.75.75v3a.75.75 0 01-1.5 0V4.06l-4.47 4.47a.75.75 0 01-1.06-1.06L11.44 3H10.25a.75.75 0 010-1.5h.01z"/></svg>'

    # JS via st.iframe() — runs in iframe, accesses parent DOM
    js = f"""
    <script>
    (function() {{
        var hostDoc = parent.document;
        var hostWin = hostDoc.defaultView || parent;

        /* Cleanup previous run */
        if (hostWin._stxBibCleanup) {{
            try {{ hostWin._stxBibCleanup(); }} catch(e) {{}}
        }}

        /* --- Icons --- */
        var ICON_COPY  = '{ICON_COPY}';
        var ICON_CHECK = '{ICON_CHECK}';
        var ICON_OPEN  = '{ICON_OPEN}';

        /* --- Create the hover card in the parent DOM --- */
        var card = hostDoc.getElementById('stx-bib-card');
        if (card) card.remove();

        card = hostDoc.createElement('div');
        card.id = 'stx-bib-card';
        card.innerHTML = [
            '<div class="stx-bib-title"></div>',
            '<div class="stx-bib-authors"></div>',
            '<div class="stx-bib-venue"></div>',
            '<div class="stx-bib-doi"></div>',
            '<div class="stx-bib-abstract"></div>',
            '<div class="stx-bib-actions">',
            '  <button class="stx-bib-btn stx-bib-btn-copy" title="Copy reference">' + ICON_COPY + ' Copy</button>',
            '  <button class="stx-bib-btn stx-bib-btn-open" title="Open in new tab" data-url="">' + ICON_OPEN + ' Open</button>',
            '</div>'
        ].join('');
        hostDoc.body.appendChild(card);

        var titleEl    = card.querySelector('.stx-bib-title');
        var authorsEl  = card.querySelector('.stx-bib-authors');
        var venueEl    = card.querySelector('.stx-bib-venue');
        var doiEl      = card.querySelector('.stx-bib-doi');
        var abstractEl = card.querySelector('.stx-bib-abstract');
        var copyBtn    = card.querySelector('.stx-bib-btn-copy');
        var openBtn    = card.querySelector('.stx-bib-btn-open');

        /* --- State: track current cite & hide timer --- */
        var currentCite = null;
        var hideTimer   = null;

        function showCard() {{
            clearTimeout(hideTimer);
            card.classList.add('visible');
        }}

        function scheduleHide() {{
            clearTimeout(hideTimer);
            hideTimer = setTimeout(function() {{
                card.classList.remove('visible');
                currentCite = null;
            }}, 250);
        }}

        /* Keep card visible when mouse enters it */
        card.addEventListener('mouseenter', function() {{ clearTimeout(hideTimer); }});
        card.addEventListener('mouseleave', scheduleHide);

        /* --- Copy button --- */
        copyBtn.addEventListener('click', function(e) {{
            e.stopPropagation();
            if (!currentCite) return;

            var c = currentCite;
            var authors = c.dataset.bibAuthors || 'Unknown';
            var year    = c.dataset.bibYear || 'n.d.';
            var title   = c.dataset.bibTitle || '';
            var journal = c.dataset.bibJournal || '';
            var volume  = c.dataset.bibVolume || '';
            var pages   = c.dataset.bibPages || '';
            var doi     = c.dataset.bibDoi || '';

            /* Build APA-style reference */
            var ref = authors + ' (' + year + '). ' + title + '.';
            if (journal) {{
                ref += ' ' + journal;
                if (volume) ref += ', ' + volume;
                if (pages) ref += ', ' + pages;
                ref += '.';
            }}
            if (doi) ref += ' https://doi.org/' + doi;

            /* Copy to clipboard */
            if (hostWin.navigator && hostWin.navigator.clipboard) {{
                hostWin.navigator.clipboard.writeText(ref).then(function() {{
                    /* Visual feedback */
                    copyBtn.innerHTML = ICON_CHECK + ' Copied!';
                    copyBtn.classList.add('copied');
                    setTimeout(function() {{
                        copyBtn.innerHTML = ICON_COPY + ' Copy';
                        copyBtn.classList.remove('copied');
                    }}, 1500);
                }}).catch(function() {{
                    fallbackCopy(ref);
                }});
            }} else {{
                fallbackCopy(ref);
            }}
        }});

        function fallbackCopy(text) {{
            var ta = hostDoc.createElement('textarea');
            ta.value = text;
            ta.style.cssText = 'position:fixed;left:-9999px';
            hostDoc.body.appendChild(ta);
            ta.select();
            hostDoc.execCommand('copy');
            hostDoc.body.removeChild(ta);
            copyBtn.innerHTML = ICON_CHECK + ' Copied!';
            copyBtn.classList.add('copied');
            setTimeout(function() {{
                copyBtn.innerHTML = ICON_COPY + ' Copy';
                copyBtn.classList.remove('copied');
            }}, 1500);
        }}

        /* --- Open button --- */
        openBtn.addEventListener('click', function(e) {{
            e.stopPropagation();
            var url = openBtn.getAttribute('data-url');
            if (url) hostWin.open(url, '_blank');
        }});

        /* --- Attach listeners to .stx-cite elements --- */
        function attachBibListeners() {{
            /* Search in parent DOM */
            var cites = Array.from(hostDoc.querySelectorAll('.stx-cite'));

            /* Also search inside iframes (st.html content) */
            var iframes = hostDoc.querySelectorAll('iframe');
            iframes.forEach(function(iframe) {{
                try {{
                    var iDoc = iframe.contentDocument || iframe.contentWindow.document;
                    var iCites = iDoc.querySelectorAll('.stx-cite');
                    iCites.forEach(function(c) {{ cites.push(c); }});
                }} catch(e) {{ /* cross-origin, skip */ }}
            }});

            cites.forEach(function(cite) {{
                if (cite.dataset.bibListener) return;
                cite.dataset.bibListener = "true";

                cite.addEventListener('mouseenter', function() {{
                    var title    = cite.dataset.bibTitle || '';
                    var authors  = cite.dataset.bibAuthors || '';
                    var year     = cite.dataset.bibYear || '';
                    var journal  = cite.dataset.bibJournal || '';
                    var doi      = cite.dataset.bibDoi || '';
                    var abstract = cite.dataset.bibAbstract || '';
                    var refUrl   = cite.dataset.bibUrl || '';

                    if (!title && !authors) return;

                    currentCite = cite;

                    titleEl.textContent = title;
                    authorsEl.textContent = authors + (year ? ' (' + year + ')' : '');
                    venueEl.textContent = journal;
                    doiEl.textContent = doi ? 'DOI: ' + doi : '';
                    doiEl.style.display = doi ? 'block' : 'none';
                    abstractEl.textContent = abstract;
                    abstractEl.style.display = abstract ? 'block' : 'none';

                    /* Update Open button visibility */
                    openBtn.setAttribute('data-url', refUrl);

                    /* Reset copy button state */
                    copyBtn.innerHTML = ICON_COPY + ' Copy';
                    copyBtn.classList.remove('copied');

                    /* Position relative to the parent viewport */
                    var rect = cite.getBoundingClientRect();
                    var offsetTop = 0, offsetLeft = 0;
                    var citeDoc = cite.ownerDocument;
                    if (citeDoc !== hostDoc) {{
                        var frameEl = citeDoc.defaultView.frameElement;
                        if (frameEl) {{
                            var frameRect = frameEl.getBoundingClientRect();
                            offsetTop = frameRect.top;
                            offsetLeft = frameRect.left;
                        }}
                    }}

                    var top  = rect.bottom + offsetTop + 8;
                    var left = rect.left + offsetLeft;
                    var winW = hostWin.innerWidth;
                    var winH = hostWin.innerHeight;

                    if (left + 420 > winW) left = winW - 440;
                    if (top + 250 > winH) top = rect.top + offsetTop - 260;
                    if (left < 10) left = 10;

                    card.style.top  = top + 'px';
                    card.style.left = left + 'px';
                    showCard();
                }});

                cite.addEventListener('mouseleave', scheduleHide);
            }});
        }}

        /* MutationObserver on parent DOM to catch dynamically added cites */
        var obs = new MutationObserver(attachBibListeners);
        obs.observe(hostDoc.body, {{ childList: true, subtree: true }});

        /* Initial scan with delay for Streamlit rendering */
        var initTimer = setTimeout(attachBibListeners, 500);

        /* Periodic scan (iframes load asynchronously) */
        var scanInterval = setInterval(attachBibListeners, 2000);

        /* Cleanup function for next hot-reload */
        hostWin._stxBibCleanup = function() {{
            obs.disconnect();
            clearTimeout(initTimer);
            clearTimeout(hideTimer);
            clearInterval(scanInterval);
            var el = hostDoc.getElementById('stx-bib-card');
            if (el) el.remove();
        }};
    }})();
    </script>
    """

    # st.iframe() creates a real iframe where scripts execute
    st.iframe(js, height=1)
