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
    "district of columbia": "DC",
}

VALID_STATES = set(STATE_MAP.values())

MONTH_MAP = {
    "jan": "01", "feb": "02", "mar": "03", "apr": "04",
    "may": "05", "jun": "06", "jul": "07", "aug": "08",
    "sep": "09", "oct": "10", "nov": "11", "dec": "12",
}


def normalize_phone(phone):
    if not phone or pd.isna(phone):
        return ""
    digits = re.sub(r"\D", "", str(phone))
    # Strip leading 1 for 11-digit numbers
    if len(digits) == 11 and digits[0] == "1":
        digits = digits[1:]
    return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}" if len(digits) == 10 else ""


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
    return upper[:2]


def normalize_email(email):
    if not email or pd.isna(email):
        return ""
    e = str(email).strip().lower()
    # Basic validation: no spaces, must have @, domain must have .
    return e if " " not in e and "@" in e and "." in e.split("@")[-1] else ""


def clean(input_path="data/messy.csv", output_path="data/cleaned.csv"):
    df = pd.read_csv(input_path, dtype=str)

    # Strip whitespace and replace sentinel values
    df = df.fillna("")
    sentinels = {"n/a", "null", "none", "nan", "#n/a", "na"}
    for col in df.columns:
        df[col] = df[col].str.strip()
        # Build comprehensive sentinel set with all case variations
        sentinel_dict = {}
        for s in sentinels:
            sentinel_dict[s] = ""
            sentinel_dict[s.upper()] = ""
            sentinel_dict[s.title()] = ""
        df[col] = df[col].replace(sentinel_dict, regex=False)

    df["name"] = df["name"].apply(lambda x: x.title() if x else "")
    df["email"] = df["email"].apply(normalize_email)
    df["phone"] = df["phone"].apply(normalize_phone)
    df["signup_date"] = df["signup_date"].apply(normalize_date)
    df["state"] = df["state"].apply(normalize_state)

    df["age"] = pd.to_numeric(df["age"], errors="coerce")
    df["salary"] = pd.to_numeric(df["salary"], errors="coerce")
    df = df[~((df["age"] < 0) | (df["age"] > 120) | (df["salary"] < 0) | (df["salary"] > 1_000_000))]
    df["age"] = df["age"].apply(lambda x: str(int(x)) if pd.notna(x) else "")
    df["salary"] = df["salary"].apply(lambda x: str(int(x)) if pd.notna(x) else "")

    df = df[df["email"] != ""]
    df = df.drop_duplicates(subset=["name", "email"], keep="first")

    df.to_csv(output_path, index=False)


if __name__ == "__main__":
    clean()
