# Auto-detect by extension
from streamtex.bib import load_bib
entries = load_bib("references.bib")   # BibTeX
entries = load_bib("refs.ris")          # RIS
entries = load_bib("refs.json")         # JSON

# Add a custom parser
from streamtex.bib import register_bib_parser

def parse_yaml(path):
    import yaml
    with open(path) as f:
        data = yaml.safe_load(f)
    return [BibEntry(key=d["key"], ...) for d in data]

register_bib_parser("yaml", parse_yaml)
