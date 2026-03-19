# Step 3 — Migrate Assets

> **Profile-independent:** Image handling is the same for both profiles.

## Workflow

1. **Inventory** all images referenced in source slide files (`![...](...)`)
2. **Copy** existing images to `static/images/day{N}/`
3. **Rename** if needed to match convention
4. **Report** missing images with:
   - Original reference path
   - Suggested generation prompt (from source comments or alt text)
   - Suggested `st_ai_image_widget()` replacement

## Image URI Rule (CRITICAL)

URIs are relative to the static source configured in `book.py`:

```python
# book.py: stx.set_static_sources([str(Path(__file__).parent / "static")])

# CORRECT
st_image(uri="images/day1/file.png", width="100%")

# WRONG — double prefix
st_image(uri="static/images/day1/file.png", width="100%")
```

## Missing Image Handling

For each missing image, generate a placeholder in the block:

```python
st_write(bs.placeholder, "[Image: description]", tag=t.div)
# IMAGE PROMPT: "description, dark background, minimalist, 16:9"
# SUGGESTED FILENAME: static/images/day2/description.png
```
