# stx-live — the Streamlit face of every site of a project (stx release): one Streamlit process per
# site under supervisord, and an nginx router (host → site → port).
#
# Rebuilt only when StreamTeX or a dependency changes: `stx-version` and `requirements.txt` are
# written by `stx release lock` from uv.lock (the version TESTED locally, never a new resolution).
# The CONTENT (the code of the documents, the media) is never in the image: it lives in the volume
# /srv/live, copied by `stx release publish`.
FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 UV_LINK_MODE=copy \
    STREAMLIT_BROWSER_GATHERUSAGESTATS=false STREAMLIT_SERVER_HEADLESS=true

RUN apt-get update && apt-get install -y --no-install-recommends nginx-light supervisor curl \
    && rm -rf /var/lib/apt/lists/*
COPY --from=ghcr.io/astral-sh/uv:0.9 /uv /bin/uv
# STX_RELEASE_APT — the project's system packages ([release] apt), or nothing

WORKDIR /app
COPY stx-version requirements.txt ./
RUN uv venv /app/.venv \
    && uv pip install --python /app/.venv/bin/python -r requirements.txt \
       "streamtex[cli]==$(tr -d '[:space:]' < stx-version)" \
    && /app/.venv/bin/python -c "import streamtex; print('streamtex', streamtex.__version__)"

# The PDF of the "Download as..." panel, online too: streamtex offers it only when playwright (in
# requirements.txt) AND its Chromium are present. Chromium and its system libraries (--with-deps) in a
# fixed folder, read by every process whatever its HOME. Cost: about 400 MB of image.
ENV PLAYWRIGHT_BROWSERS_PATH=/opt/ms-playwright
RUN if /app/.venv/bin/python -c "import playwright" 2>/dev/null; then \
      /app/.venv/bin/python -m playwright install --with-deps chromium && rm -rf /var/lib/apt/lists/*; \
    fi

COPY nginx.conf /etc/nginx/nginx.conf
# The versions shipped by the image; the ones in service live on the server disk (entrypoint.sh).
COPY stx-http.conf /opt/stx/stx-http.conf
COPY stx_auth.py /opt/stx/stx_auth.py
COPY stx_auth_lib.py /opt/stx/stx_auth_lib.py
COPY supervisord.conf /etc/supervisor/supervisord.conf
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

EXPOSE 80
HEALTHCHECK CMD curl -fs http://127.0.0.1/_health || exit 1
ENTRYPOINT ["/app/entrypoint.sh"]
