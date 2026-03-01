with st.form("bck26_validation_form"):
    password = st.text_input("Enter a password", type="password")
    validated = st.form_submit_button("Validate")
if validated:
    if len(password) >= 8:
        with st_block(s.project.containers.good_callout):
            st_write(s.project.titles.tip_label, "Valid")
            st_space("v", 1)
            st_write(s.large, "Strong password!")
    else:
        with st_block(s.project.containers.bad_callout):
            st_write(s.project.titles.warning_label, "Invalid")
            st_space("v", 1)
            st_write(s.large,
                     f"Too short ({len(password)}/8 characters).")
