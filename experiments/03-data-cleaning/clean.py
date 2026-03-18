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

VALID_STATES = set(STATE_MAP.values())

MONTH_MAP = {
    "jan": "01", "feb": "02", "mar": "03", "apr": "04",
    "may": "05", "jun": "06", "jul": "07", "aug": "08",
    "sep": "09", "oct": "10", "nov": "11", "dec": "12",
}

SENTINEL_VALUES = {
    "n/a", "N/A", "na", "NA", "Na",
    "null", "NULL", "Null",
    "none", "NONE", "None",
    "nan", "NAN", "Nan"
}


def normalize_phone(phone):
    if pd.isna(phone) or phone == "":
        return ""
    digits = re.sub(r"\D", "", str(phone))
    digits = digits[1:] if len(digits) == 11 and digits.startswith("1") else digits
    return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}" if len(digits) == 10 else ""


def normalize_date(s):
    if pd.isna(s) or s == "":
        return ""
    s = str(s).split("T")[0]  # Handle ISO timestamp format
    # Already in correct format
    if re.match(r"^\d{4}-\d{2}-\d{2}$", s):
        return s
    # MM/DD/YYYY format
    if m := re.match(r"^(\d{1,2})/(\d{1,2})/(\d{4})$", s):
        return f"{m.group(3)}-{int(m.group(1)):02d}-{int(m.group(2)):02d}"
    # Mon DD YYYY format
    if m := re.match(r"^([A-Za-z]{3})\s+(\d{1,2})\s+(\d{4})$", s):
        if mon := MONTH_MAP.get(m.group(1).lower()):
            return f"{m.group(3)}-{mon}-{int(m.group(2)):02d}"
    # DD-MM-YYYY format
    if m := re.match(r"^(\d{1,2})-(\d{1,2})-(\d{4})$", s):
        return f"{m.group(3)}-{int(m.group(2)):02d}-{int(m.group(1)):02d}"
    return ""


def normalize_state(state):
    if pd.isna(state) or state == "":
        return ""
    s = str(state).lower()
    if mapped := STATE_MAP.get(s):
        return mapped
    # Check if it's a valid 2-letter state code, only compute upper() if length is 2
    if len(s) == 2 and (upper := s.upper()) in VALID_STATES:
        return upper
    return ""


def normalize_email(email):
    if pd.isna(email) or email == "":
        return ""
    e = str(email).lower()
    return e if "@" in e and " " not in e else ""


def clean(input_path="data/messy.csv", output_path="data/cleaned.csv"):
    df = pd.read_csv(input_path, dtype=str)

    # Strip whitespace and replace sentinels in one pass
    for col in df.columns:
        df[col] = df[col].str.strip()
        df[col] = df[col].where(~df[col].isin(SENTINEL_VALUES), "")

    # Normalize all fields first
    df["name"] = df["name"].str.title()
    df["email"] = df["email"].apply(normalize_email)
    df["phone"] = df["phone"].apply(normalize_phone)
    df["signup_date"] = df["signup_date"].apply(normalize_date)
    df["state"] = df["state"].apply(normalize_state)

    # Outlier filtering and numeric conversion
    for col, min_val, max_val in [("age", 0, 120), ("salary", 0, 1_000_000)]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        df = df[df[col].isna() | df[col].between(min_val, max_val)]
        df[col] = df[col].apply(lambda x: str(int(x)) if pd.notna(x) else "")

    # Filter and deduplicate AFTER all normalization is complete
    df = df[df["email"] != ""]
    df = df.drop_duplicates(subset=["name", "email"], keep="first")

    df.to_csv(output_path, index=False)


if __name__ == "__main__":
    clean()
