"""Server-side pieces of a deployed StreamTeX site.

Modules here run inside the deployment container, next to nginx, and use
only the Python standard library: the generated Dockerfile copies them out
of the installed package so that they start without importing streamlit.
"""
