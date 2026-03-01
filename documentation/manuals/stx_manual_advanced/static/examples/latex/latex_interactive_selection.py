examples = {"Simple": code1, "Lists": code2, "Math": code3, ...}
choice = st.selectbox("Choose a document", list(examples.keys()))
stx.st_latex_doc(examples[choice], height=400)
