# blocks/_atomic/bck_grades.py
from streamtex import *
from streamtex import GSheetSource, load_gsheet_df, GSheetConfig, AuthMode
import streamtex as stx

_src = GSheetSource.from_url(
    "https://docs.google.com/spreadsheets/d/1BxiMk.../edit",
    tab="Notes",
)

def build():
    df = load_gsheet_df(_src, config=GSheetConfig(auth_mode=AuthMode.PUBLIC))
    stx.st_dataframe(df)
    stx.st_bar_chart(df, x="Student", y="Grade")
