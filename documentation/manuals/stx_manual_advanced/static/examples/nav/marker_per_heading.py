# Exclude a heading from markers (e.g. appendix)
st_write(s.huge, "Appendix", toc_lvl="1", marker=False)

# Force a heading to become a marker even when auto is off
st_write(s.huge, "Important Note", toc_lvl="2", marker=True)
