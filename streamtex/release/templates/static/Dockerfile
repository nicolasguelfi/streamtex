# stx-static — nginx and the login service, for the HTML face of every site of a project (stx release).
# Rebuilt rarely: the configuration lives on the server disk (/srv/static/conf), the content in the volume.
FROM nginx:1.29-alpine
# python3: the login service (stx_auth), standard library only.
RUN apk add --no-cache python3
COPY nginx.conf /etc/nginx/nginx.conf
# The versions shipped by the image; the ones in service live on the server disk (10-stx-init.sh).
COPY stx-http.conf /opt/stx/stx-http.conf
COPY stx_auth.py /opt/stx/stx_auth.py
COPY stx_auth_lib.py /opt/stx/stx_auth_lib.py
COPY closed.html /opt/stx/closed.html
COPY 20-stx-auth.sh /docker-entrypoint.d/20-stx-auth.sh
# The volume may be empty on first start: nginx must start anyway.
COPY 10-stx-init.sh /docker-entrypoint.d/10-stx-init.sh
EXPOSE 80
HEALTHCHECK CMD wget -qO- http://127.0.0.1/_health || exit 1
