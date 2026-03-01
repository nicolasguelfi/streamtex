from streamtex import GSheetConfig, AuthMode, set_gsheet_config

# Public sheets (no authentication needed)
cfg = GSheetConfig(auth_mode=AuthMode.PUBLIC, cache_ttl=600)

# Service account (server-side, recommended for deploy)
cfg = GSheetConfig(
    auth_mode=AuthMode.SERVICE_ACCOUNT,
    credentials_path="credentials.json",  # or use env var
    cache_ttl=300,
)

# OAuth2 fallback (interactive browser auth)
cfg = GSheetConfig(
    auth_mode=AuthMode.OAUTH2,
    credentials_path="client_secret.json",
)

set_gsheet_config(cfg)
