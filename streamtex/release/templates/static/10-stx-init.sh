#!/bin/sh
# The volume mounted on /srv/static may be empty (first start): put there, when missing, the
# configuration and the login service shipped by the image. Then `stx release server-config`
# keeps them up to date on the disk.
mkdir -p /srv/static/conf /srv/static/sites
[ -f /srv/static/conf/stx-http.conf ] || cp /opt/stx/stx-http.conf /srv/static/conf/stx-http.conf
[ -f /srv/static/conf/stx_auth.py ] || cp /opt/stx/stx_auth.py /srv/static/conf/stx_auth.py
[ -f /srv/static/conf/stx_auth_lib.py ] || cp /opt/stx/stx_auth_lib.py /srv/static/conf/stx_auth_lib.py
[ -f /srv/static/conf/closed.html ] || cp /opt/stx/closed.html /srv/static/conf/closed.html
