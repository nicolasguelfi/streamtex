from streamtex import GSheetSource, load_gsheet, load_gsheet_df

# From sheet ID
src = GSheetSource(sheet_id="1BxiMk...", tab="Notes", range="A1:E30")

# From URL
src = GSheetSource.from_url(
    "https://docs.google.com/spreadsheets/d/1BxiMk.../edit",
    tab="Notes",
)

# Load as list of dicts
data = load_gsheet(src)

# Load as pandas DataFrame
df = load_gsheet_df(src)
