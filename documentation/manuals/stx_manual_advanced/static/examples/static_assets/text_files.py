text_path = os.path.join("static", "texts", "sample_lorem.txt")
with open(text_path) as f:
    content = f.read()
stx.st_code(code=content, language="text")
