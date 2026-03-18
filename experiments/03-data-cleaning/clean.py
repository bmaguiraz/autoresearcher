"""Data cleaning script — the agent edits this file to improve quality scores."""

import re
import pandas as pd

STATE_MAP = {
    "alabama": "AL", "alaska": "AK", "arizona": "AZ", "arkansas": "AR",
    "california": "CA", "calif.": "CA", "colorado": "CO", "connecticut": "CT",
    "delaware": "DE", "florida": "FL", "georgia": "GA", "hawaii": "HI",
    "idaho": "ID", "illinois": "IL", "indiana": "IN", "iowa": "IA",
    "kansas": "KS", "kentucky": "KY", "louisiana": "LA", "maine": "ME",
    "maryland": "MD", "massachusetts": "MA", "michigan": "MI", "minnesota": "MN",
    "mississippi": "MS", "missouri": "MO", "montana": "MT", "nebraska": "NE",
    "nevada": "NV", "new hampshire": "NH", "new jersey": "NJ", "new mexico": "NM",
    "new york": "NY", "north carolina": "NC", "north dakota": "ND", "ohio": "OH",
    "oklahoma": "OK", "oregon": "OR", "pennsylvania": "PA", "rhode island": "RI",
    "south carolina": "SC", "south dakota": "SD", "tennessee": "TN", "texas": "TX",
    "utah": "UT", "vermont": "VT", "virginia": "VA", "washington": "WA",
    "west virginia": "WV", "wisconsin": "WI", "wyoming": "WY",
    "district of columbia": "DC", "d.c.": "DC",
}

MONTH_MAP = {
    "jan": "01", "feb": "02", "mar": "03", "apr": "04",
    "may": "05", "jun": "06", "jul": "07", "aug": "08",
    "sep": "09", "oct": "10", "nov": "11", "dec": "12",
}

SENTINEL_LOWER = {"n/a", "na", "null", "none", "nan"}


def normalize_phone(phone):
    if pd.isna(phone) or phone == "":
        return ""
    digits = re.sub(r"\D", "", str(phone))
    digits = digits[1:] if len(digits) == 11 and digits[0] == "1" else digits
    return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}" if len(digits) == 10 else ""


def normalize_date(s):
    if pd.isna(s) or s == "":
        return ""
    s = str(s).split("T")[0]
    if len(s) == 10 and s[4] == '-' and s[7] == '-':
        return s
    if m := re.match(r"^(\d{1,2})/(\d{1,2})/(\d{4})$", s):
        return f"{m.group(3)}-{int(m.group(1)):02d}-{int(m.group(2)):02d}"
    if m := re.match(r"^([A-Za-z]{3})\s+(\d{1,2})\s+(\d{4})$", s):
        if mon := MONTH_MAP.get(m.group(1).lower()):
            return f"{m.group(3)}-{mon}-{int(m.group(2)):02d}"
    if m := re.match(r"^(\d{1,2})-(\d{1,2})-(\d{4})$", s):
        return f"{m.group(3)}-{int(m.group(2)):02d}-{int(m.group(1)):02d}"
    return ""


def normalize_state(state):
    if pd.isna(state) or state == "":
        return ""
    s = str(state).lower()
    if mapped := STATE_MAP.get(s):
        return mapped
    upper = s.upper()
    if len(s) == 2 and upper in STATE_MAP.values():
        return upper
    return ""


def normalize_email(email):
    if pd.isna(email) or email == "":
        return ""
    e = str(email).lower()
    return e if "@" in e and " " not in e else ""


def clean(input_path="data/messy.csv", output_path="data/cleaned.csv"):
    df = pd.read_csv(input_path, dtype=str)

    for col in df.columns:
        stripped = df[col].str.strip()
        df[col] = stripped.where(~stripped.str.lower().isin(SENTINEL_LOWER), "")

    df["name"] = df["name"].str.title()
    df["email"] = df["email"].apply(normalize_email)
    df["phone"] = df["phone"].apply(normalize_phone)
    df["signup_date"] = df["signup_date"].apply(normalize_date)
    df["state"] = df["state"].apply(normalize_state)

    for col, min_val, max_val in [("age", 0, 120), ("salary", 0, 1_000_000)]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        df = df[df[col].isna() | df[col].between(min_val, max_val)]
        df[col] = df[col].apply(lambda x: "" if pd.isna(x) else str(int(x)))

    df = df[df["email"] != ""]
    df = df.drop_duplicates(subset=["name", "email"], keep="first")

    df.to_csv(output_path, index=False)


if __name__ == "__main__":
    clean()
