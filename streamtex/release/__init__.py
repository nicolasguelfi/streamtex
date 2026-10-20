"""stx release — publish the documents of a multi-document project (#136, #111).

Taken from the streamtex-all-trainings prototype (``_project/deploy/release``), its server layout kept
exactly. A project runs two long-lived Coolify applications: a static one (nginx, the HTML exports) and
a live one (one Streamlit process per site under supervisord, an nginx router host → site → port). A
*site* is one document with up to two *faces* (``live``, ``html``), published together, all or nothing:
code snapshot → HTML export on this machine, checked → copy of the delta over SSH (``rsync
--link-dest``) → passwords → both faces switch together → restart of that site's process only → check
of what is actually served, and back to the previous snapshot when a check fails.

Modules: ``config`` (``[release]`` of stx.toml, the site list), ``state`` (``.stx-release.json``,
versioned, no secret), ``target`` (where to publish: ``local`` Docker or ``ssh``), ``passwords``
(``.stx-passwords.toml`` per site), ``build`` (snapshot and export), ``ops`` (publish, status,
rollback, …), ``coolify`` (the two applications and their domains).
"""

import click


class ReleaseError(click.ClickException):
    """A refused release step: a clear message, exit code 1, nothing changed on the server."""
