# Simple spacing with st_br
st_write(s.large, "Paragraph 1")
st_br()
st_write(s.large, "Paragraph 2")

# Explicit spacing with st_space
st_write(s.large, "Section 1")
st_space("v", 3)  # More space
st_write(s.large, "Section 2")