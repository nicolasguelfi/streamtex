st_write(s.Large, "My Title", toc_lvl="1")        # absolute level
st_write(s.large, "Sub", toc_lvl="+1")            # relative level
st_write(s.large, "Custom Label", toc_lvl="2", label="Short")
