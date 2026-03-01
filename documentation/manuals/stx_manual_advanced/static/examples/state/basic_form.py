with st.form("bck26_profile_form"):
    name = st.text_input("Name", value="Ada Lovelace")
    age = st.number_input("Age", 0, 120, 25)
    submitted = st.form_submit_button("Submit")
if submitted:
    with st_block(s.project.containers.result_box):
        st_write(s.large + s.bold, f"Name: {name}")
        st_br()
        st_write(s.large, f"Age: {age}")
