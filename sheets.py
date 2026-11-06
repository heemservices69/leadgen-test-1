"""Google Sheets output via a service account (gspread)."""
import gspread, pandas as pd
import config

COLUMNS = ["name", "category", "city", "phone", "email", "website", "facebook", "instagram",
           "linkedin", "address", "maps_link", "ai_score", "best_service", "ai_reason",
           "pitch", "source", "status"]

def push(df: pd.DataFrame, sheet_id: str, tab: str = "Leads") -> int:
    gc = gspread.service_account_from_dict(config.service_account_info())
    sh = gc.open_by_key(sheet_id)
    try:
        ws = sh.worksheet(tab)
    except gspread.WorksheetNotFound:
        ws = sh.add_worksheet(tab, rows=1000, cols=len(COLUMNS))
    if not ws.get_all_values():
        ws.append_row(COLUMNS)
    existing = ws.get_all_records()
    seen = {(r.get("name", "").lower(), str(r.get("phone", ""))) for r in existing}
    rows = []
    for _, r in df.iterrows():
        k = (str(r.get("name", "")).lower(), str(r.get("phone", "")))
        if k in seen:
            continue
        rows.append([str(r.get(c, "") if pd.notna(r.get(c, "")) else "") for c in COLUMNS[:-1]] + ["New"])
    if rows:
        ws.append_rows(rows, value_input_option="USER_ENTERED")
    return len(rows)
