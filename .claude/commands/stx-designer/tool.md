# /stx-designer:tool — Run a specialized tool

Arguments: $ARGUMENTS

## Argument parsing

Parse `$ARGUMENTS` as: `<tool-name> <description>`

**Tool name**: The first word of `$ARGUMENTS` identifies the tool.
**Description**: The remaining text provides context, paths, or options.

Special cases:
- `--help` — Show the stx-designer cheatsheet (see init.md Help section)
- Empty or `list` — List all available tools

### Examples

```
/stx-designer:tool list
/stx-designer:tool survey-convert
/stx-designer:tool survey-convert --all temp/
/stx-designer:tool survey-convert temp/Screenshot_IDE.png
/stx-designer:tool --help
```

## Tool resolution

Tools are defined in `.claude/designer/tools/<tool-name>.md`. Each tool file contains
the complete instructions for that tool.

### Workflow

1. **Parse tool name** from `$ARGUMENTS`
2. **If no tool name or "list"**: List available tools from `.claude/designer/tools/` directory
3. **If tool file exists**: Read `.claude/designer/tools/<tool-name>.md` and execute its instructions, passing the remaining description as context
4. **If tool file does not exist**: Report the error and list available tools

### Listing tools

When listing tools, show:

```
Available stx-designer tools:

  survey-convert   Convert survey screenshots to code-generated chart blocks
  list             List all available tools

Usage: /stx-designer:tool <tool-name> [options] [description]
```

## Built-in tools

### survey-convert

Convert Stack Overflow Developer Survey screenshots into code-generated StreamTeX blocks.

**Tool file**: `.claude/designer/tools/survey-convert.md`

**Syntax**:
```
/stx-designer:tool survey-convert [OPTIONS] [SOURCE]
```

**Options**:
- `--all` — Convert ALL images in the source directory (batch mode)
- `--list` — List all images in the source directory (no conversion)

**Source**:
- A single image path: Convert that one image
- A directory path: Use as source directory
- Omitted: Default to the project's `temp/` directory

**Output**: Creates `blocks/bck_survey_<topic>.py` with data-driven bar chart rendering.

---

## Adding new tools

To add a new tool to the stx-designer ecosystem:

1. Create `.claude/designer/tools/<tool-name>.md` in the profile
2. The file should contain:
   - Description of what the tool does
   - Required readings (skills, references)
   - Step-by-step workflow
   - Output format
3. The tool will automatically appear in `/stx-designer:tool list`
4. Update the manifest if the tool needs to be installed with the profile

## Constraints

- Tools are self-contained — each tool file has all the instructions needed
- Tools should NOT duplicate functionality available in init/update/audit/fix
- Tools are for specialized, domain-specific operations
