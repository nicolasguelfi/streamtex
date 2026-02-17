"""Link preview scaffold: hover card JS/CSS injection and page preview fetching."""

import textwrap
import streamlit as st
import requests
from requests.exceptions import ConnectionError, Timeout
from bs4 import BeautifulSoup as bs


def _get_page_preview(url: str):
    """
    Fetches the page title and favicon URL for the given link.
    If the connection is refused or times out, returns defaults preventing display of any preview.
    """
    title = url
    favicon = 'https://www.google.com/s2/favicons?domain_url=' + url
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        soup = bs(response.content, 'html.parser')

        title = soup.title.string.strip() if soup.title else 'No title found'

        favicon = None
        icon_link = soup.find('link', rel=lambda x: x and 'icon' in x.lower())
        if icon_link and icon_link.get('href'):
            favicon = icon_link['href']
            if favicon.startswith('//'):
                favicon = 'http:' + favicon
            elif favicon.startswith('/'):
                from urllib.parse import urljoin
                favicon = urljoin(url, favicon)
        else:
            favicon = 'https://www.google.com/s2/favicons?domain_url=' + url

        return title, favicon, True

    except (ConnectionError, Timeout):
        return title, favicon, False

    except Exception:
        return 'Could not fetch page', None, False


def inject_link_preview_scaffold():
    """Injects the hidden Tooltip container and the JS event listeners."""

    css = """
    <style>
        #streamtex-preview-card {
            position: fixed;
            z-index: 999999;
            display: none;
            width: 280px;
            background: white;
            border-radius: 8px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.15);
            border: 1px solid #e0e0e0;
            font-family: sans-serif;
            padding: 12px;
            pointer-events: none;
            opacity: 0;
            transition: opacity 0.15s ease;
        }
        #streamtex-preview-card.visible { display: block; opacity: 1; }
        .st-card-row { display: flex; align-items: center; gap: 10px; }
        .st-card-favicon { width: 20px; height: 20px; border-radius: 4px; }
        .st-card-content { display: flex; flex-direction: column; overflow: hidden; }
        .st-card-title { font-size: 14px; font-weight: 600; color: #333; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }
        .st-card-url { font-size: 11px; color: #1a73e8; overflow: hidden; white-space: nowrap; text-overflow: ellipsis; }
    </style>
    """

    js = textwrap.dedent("""
    <script>
    (function() {
        console.log("StreamTeX: Init");

        var existing = document.getElementById('streamtex-preview-card');
        if (!existing) {
            var card = document.createElement('div');
            card.id = 'streamtex-preview-card';

            var row = document.createElement('div');
            row.className = 'st-card-row';

            var img = document.createElement('img');
            img.className = 'st-card-favicon';

            var content = document.createElement('div');
            content.className = 'st-card-content';

            var titleSpan = document.createElement('span');
            titleSpan.className = 'st-card-title';
            titleSpan.textContent = 'Loading...';

            var urlSpan = document.createElement('span');
            urlSpan.className = 'st-card-url';

            content.appendChild(titleSpan);
            content.appendChild(urlSpan);
            row.appendChild(img);
            row.appendChild(content);
            card.appendChild(row);

            document.body.appendChild(card);
        }

        var card = document.getElementById('streamtex-preview-card');
        var cardImg = card.querySelector('.st-card-favicon');
        var cardTitle = card.querySelector('.st-card-title');
        var cardUrl = card.querySelector('.st-card-url');

        function attachListeners() {
            var links = document.querySelectorAll('a.streamtex-link');

            links.forEach(function(link) {
                if (link.dataset.hasListener) return;
                link.dataset.hasListener = "true";

                link.addEventListener('mouseenter', function() {
                    var href = link.href;
                    if (!href) return;

                    try {
                        var urlObj = new URL(href);
                        cardImg.src = 'https://www.google.com/s2/favicons?domain_url=' + href + '&sz=64';
                        cardTitle.textContent = urlObj.hostname;
                        cardUrl.textContent = href;

                        var rect = link.getBoundingClientRect();
                        var top = rect.bottom + 8;
                        var left = rect.left;

                        if (left + 280 > window.innerWidth) left = window.innerWidth - 300;
                        if (top + 80 > window.innerHeight) top = rect.top - 90;

                        card.style.top = top + 'px';
                        card.style.left = left + 'px';
                        card.classList.add('visible');
                    } catch (e) { console.log(e); }
                });

                link.addEventListener('mouseleave', function() {
                    card.classList.remove('visible');
                });
            });
        }

        if (window.stxObs) window.stxObs.disconnect();
        window.stxObs = new MutationObserver(attachListeners);
        window.stxObs.observe(document.body, { childList: true, subtree: true });

        setTimeout(attachListeners, 500);
        console.log("StreamTeX: Ready");
    })();
    </script>
    """)

    st.html(css)
    st.html(js)


def contain_link(html_content="", link="", no_link_decor=False, hover=True):
    """Wraps the given HTML content in an anchor tag, optionally adding a hover preview class."""
    if not link:
        return html_content

    clean_link = link.strip()
    is_internal = clean_link.startswith("#")

    css_classes = ""
    if hover and not is_internal:
        css_classes = ' class="streamtex-link"'

    style_attr = ""
    if no_link_decor:
        style_attr = ' style="text-decoration: none; color: inherit;"'

    return f'<a href="{clean_link}"{css_classes}{style_attr}>{html_content}</a>'
