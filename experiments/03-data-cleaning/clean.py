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
}

VALID_STATES = set(STATE_MAP.values())

MONTH_MAP = {
    "jan": "01", "feb": "02", "mar": "03", "apr": "04",
    "may": "05", "jun": "06", "jul": "07", "aug": "08",
    "sep": "09", "oct": "10", "nov": "11", "dec": "12",
}


def normalize_phone(phone):
    if pd.isna(phone) or phone == "":
        return ""
    digits = re.sub(r"\D", "", str(phone))
    if digits.startswith("1") and len(digits) == 11:
        digits = digits[1:]
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    return ""


def normalize_date(s):
    if pd.isna(s) or s == "":
        return ""
    s = str(s).strip()
    m = re.match(r"^(\d{4})-(\d{2})-(\d{2})$", s)
    if m:
        return s
    m = re.match(r"^(\d{1,2})/(\d{1,2})/(\d{4})$", s)
    if m:
        return f"{m.group(3)}-{int(m.group(1)):02d}-{int(m.group(2)):02d}"
    m = re.match(r"^([A-Za-z]{3})\s+(\d{1,2})\s+(\d{4})$", s)
    if m:
        mon = MONTH_MAP.get(m.group(1).lower()[:3])
        if mon:
            return f"{m.group(3)}-{mon}-{int(m.group(2)):02d}"
    m = re.match(r"^(\d{1,2})-(\d{1,2})-(\d{4})$", s)
    if m:
        return f"{m.group(3)}-{int(m.group(2)):02d}-{int(m.group(1)):02d}"
    return ""


def normalize_state(state):
    if pd.isna(state) or state == "":
        return ""
    s = str(state).strip().lower()
    if s in STATE_MAP:
        return STATE_MAP[s]
    upper = s.upper()
    if len(s) == 2 and upper in VALID_STATES:
        return upper
    return ""


def normalize_email(email):
    if pd.isna(email) or email == "":
        return ""
    e = str(email).strip().lower()
    if " " in e or "@" not in e or "." not in e.split("@")[-1]:
        return ""
    return e


def clean(input_path="data/messy.csv", output_path="data/cleaned.csv"):
    df = pd.read_csv(input_path, dtype=str)

    # Strip whitespace from all columns
    for col in df.columns:
        df[col] = df[col].str.strip()

    # Replace common sentinel values with empty strings
    sentinels = {"n/a", "null", "none", "nan", "#n/a", "na", "", "missing", "unknown", "n.a.", "n\\a"}
    for col in df.columns:
        df[col] = df[col].apply(lambda x: "" if str(x).strip().lower() in sentinels else x)

    df["name"] = df["name"].apply(lambda x: x.title() if x else "")
    df["email"] = df["email"].apply(normalize_email)

    # Filter and deduplicate early on normalized key fields
    df = df[df["email"] != ""]
    df = df.drop_duplicates(subset=["name", "email"], keep="first")

    df["phone"] = df["phone"].apply(normalize_phone)
    df["signup_date"] = df["signup_date"].apply(normalize_date)
    df["state"] = df["state"].apply(normalize_state)

    df["age"] = pd.to_numeric(df["age"], errors="coerce")
    df["salary"] = pd.to_numeric(df["salary"], errors="coerce")
    df = df[~((df["age"] < 0) | (df["age"] > 120))]
    df = df[~((df["salary"] < 0) | (df["salary"] > 1_000_000))]
    df["age"] = df["age"].apply(lambda x: str(int(x)) if pd.notna(x) else "")
    df["salary"] = df["salary"].apply(lambda x: str(int(x)) if pd.notna(x) else "")

    df.to_csv(output_path, index=False)


if __name__ == "__main__":
    clean()
