"""stx_auth launcher — runs the library's login service (streamtex/deploy/stx_auth.py) unchanged.

`stx release server-config` puts the library file next to this one as `stx_auth_lib.py`. This launcher
maps the applications' environment (STX_STATIC_ROOT: /srv/static or /srv/live, set by the image) to the
library's (STX_AUTH_ROOT); the site, the cookie, the form address and the home page come in nginx's
headers (X-Stx-Site, X-Stx-Cookie, X-Stx-Login, X-Stx-Home: stx-http.conf). `conf/session.key` is kept.
"""
import os
import runpy
from pathlib import Path

HERE = Path(__file__).resolve().parent
os.environ.setdefault("STX_AUTH_ROOT", os.environ.get("STX_STATIC_ROOT", str(HERE.parent)))
runpy.run_path(str(HERE / "stx_auth_lib.py"), run_name="__main__")
