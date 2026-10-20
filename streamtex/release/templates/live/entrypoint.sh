#!/bin/sh
# The volume may be empty (first start): nginx and supervisord must start. Put there too, when
# missing, the nginx configuration and the login service shipped by the image; then
# `stx release server-config` keeps them up to date on the disk.
set -e
mkdir -p /srv/live/conf/programs /srv/live/sites /srv/live/media
[ -f /srv/live/conf/ports.map ] || : > /srv/live/conf/ports.map
[ -f /srv/live/conf/stx-http.conf ] || cp /opt/stx/stx-http.conf /srv/live/conf/stx-http.conf
[ -f /srv/live/conf/stx_auth.py ] || cp /opt/stx/stx_auth.py /srv/live/conf/stx_auth.py
[ -f /srv/live/conf/stx_auth_lib.py ] || cp /opt/stx/stx_auth_lib.py /srv/live/conf/stx_auth_lib.py
exec supervisord -c /etc/supervisor/supervisord.conf
