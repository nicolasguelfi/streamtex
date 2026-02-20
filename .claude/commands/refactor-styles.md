Audit and refactor styles in the specified block file: $ARGUMENTS

1. Read the target block file
2. Identify repeated style patterns that should be extracted to `BlockStyles` or `custom/styles.py`
3. Check for inline CSS strings that should use Style composition
4. Verify style naming follows conventions (English-only, generic, descriptive)
5. Apply the refactoring, ensuring backward compatibility
6. Run `uv run pytest tests/ -v` to verify nothing broke
