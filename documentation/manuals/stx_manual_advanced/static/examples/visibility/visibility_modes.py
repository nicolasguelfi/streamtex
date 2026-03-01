# Visible
st_write(s.bold + s.large + s.project.colors.success_green,
         "s.visibility.visible:")
st_space("v", 1)
with st_span():
    with st_block(bs.demo_box
                  + s.container.bg_colors.light_blue_bg):
        st_write("Box A")
    with st_block(bs.demo_box
                  + s.container.bg_colors.light_green_bg
                  + s.visibility.visible):
        st_write("Box B (visible)")
    with st_block(bs.demo_box
                  + s.container.bg_colors.light_coral_bg):
        st_write("Box C")
st_space("v", 2)

# Invisible (space preserved)
st_write(s.bold + s.large + s.project.colors.highlight_amber,
         "s.visibility.invisible:")
st_space("v", 1)
with st_span():
    with st_block(bs.demo_box
                  + s.container.bg_colors.light_blue_bg):
        st_write("Box A")
    with st_block(bs.demo_box
                  + s.container.bg_colors.light_green_bg
                  + s.visibility.invisible):
        st_write("Box B (invisible)")
    with st_block(bs.demo_box
                  + s.container.bg_colors.light_coral_bg):
        st_write("Box C")
st_space("v", 2)

# Hidden (removed from layout)
st_write(s.bold + s.large + s.project.colors.warning_red,
         "s.visibility.hidden:")
st_space("v", 1)
with st_span():
    with st_block(bs.demo_box
                  + s.container.bg_colors.light_blue_bg):
        st_write("Box A")
    with st_block(bs.demo_box
                  + s.container.bg_colors.light_green_bg
                  + s.visibility.hidden):
        st_write("Box B (hidden)")
    with st_block(bs.demo_box
                  + s.container.bg_colors.light_coral_bg):
        st_write("Box C")
