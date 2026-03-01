examples = {"Basic": md1, "Tables": md2, "Math": md3, ...}
choice = st.selectbox("Choose an example", list(examples.keys()))
stx.st_markdown(examples[choice])
