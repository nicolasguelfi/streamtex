if "bck30_step" not in st.session_state:
    st.session_state.bck30_step = 1
step = st.session_state.bck30_step

steps_data = [
    ("Step 1: Choose your project name",
     s.project.containers.tip_callout),
    ("Step 2: Configure your styles",
     s.project.containers.note_callout),
    ("Step 3: Build your blocks",
     s.project.containers.good_callout),
]

for i, (label, callout) in enumerate(steps_data):
    if step > i:
        with st_block(callout):
            st_write(s.large + s.bold, label)

col_prev, col_next, col_reset = st.columns(3)
if col_prev.button("Previous", key="bck30_prev",
                   disabled=(step <= 1)):
    st.session_state.bck30_step -= 1
    st.rerun()
if col_next.button("Next", key="bck30_next",
                   disabled=(step >= 3)):
    st.session_state.bck30_step += 1
    st.rerun()
if col_reset.button("Reset", key="bck30_reset"):
    st.session_state.bck30_step = 1
    st.rerun()
