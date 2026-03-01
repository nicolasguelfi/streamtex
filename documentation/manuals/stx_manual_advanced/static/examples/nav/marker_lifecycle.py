# Lifecycle in book.py (simplified)
reset_marker_registry(marker_config)  # 1. Init registry

for block in blocks:                   # 2. Render blocks
    st_include(block)                  #    (st_write auto-registers markers)

inject_marker_navigation()             # 3. Emit widget + JS
