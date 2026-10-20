#!/bin/sh
# The login service (stx_auth), started before nginx and started again when it stops or when
# `stx release server-config` stops it to load a new version (read from the server disk).
# Without it, nginx answers "closed" everywhere (auth_request fails): a failure protects.
(
  while true; do
    python3 /srv/static/conf/stx_auth.py
    echo "stx_auth: stopped, starting again in 1 s" >&2
    sleep 1
  done
) &
