choice = st.radio("Pick a callout style",
                  ["Good", "Bad", "Tip", "Note"],
                  key="bck25_radio", horizontal=True)
callout_map = {
    "Good": s.project.containers.good_callout,
    "Bad": s.project.containers.bad_callout,
    "Tip": s.project.containers.tip_callout,
    "Note": s.project.containers.note_callout,
}
with st_block(callout_map[choice]):
    st_write(s.large, f"This is a {choice} callout.")
