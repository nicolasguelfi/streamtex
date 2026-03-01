from streamtex import st_marker

# Visible marker — dashed border + label text
st_marker("Section Start", visible=True)

# Invisible marker — zero height, navigation only
st_marker("Hidden Waypoint")

# Auto-generated label when omitted
st_marker()  # label = "Marker N"
