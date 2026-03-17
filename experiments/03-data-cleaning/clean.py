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


def normalize_phone(phone):
    if pd.isna(phone) or phone == "":
        return ""
    digits = re.sub(r"\D", "", str(phone))
    if digits.startswith("1") and len(digits) == 11:
        digits = digits[1:]
    if len(digits) == 10:
        return f"({digits[:3]}) {digits[3:6]}-{digits[6:]}"
    return ""


def normalize_date(date_str):
    if pd.isna(date_str) or date_str == "":
        return ""
    from dateutil import parser
    try:
        return parser.parse(str(date_str).strip(), dayfirst=False).strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        pass
    try:
        return parser.parse(str(date_str).strip(), dayfirst=True).strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        return ""


def normalize_state(state):
    if pd.isna(state) or state == "":
        return ""
    s = str(state).strip().lower()
    if s in STATE_MAP:
        return STATE_MAP[s]
    if len(s) == 2 and s.upper() in STATE_MAP.values():
        return s.upper()
    return str(state).strip().upper()[:2]


def normalize_email(email):
    if pd.isna(email) or email == "":
        return ""
    e = str(email).strip().lower()
    if " " in e:
        return ""
    if "@" not in e or "." not in e.split("@")[-1]:
        return ""
    return e


def clean(input_path="data/messy.csv", output_path="data/cleaned.csv"):
    df = pd.read_csv(input_path, dtype=str)

    for col in df.columns:
        df[col] = df[col].str.strip()

    # Replace all sentinel null values with empty string using case-insensitive match
    sentinels = {"n/a", "null", "none", "nan", "#n/a", "na", ""}
    for col in df.columns:
        df[col] = df[col].apply(lambda x: "" if str(x).strip().lower() in sentinels else x)

    df["name"] = df["name"].apply(lambda x: x.title() if x else "")
    df["email"] = df["email"].apply(normalize_email)
    df["phone"] = df["phone"].apply(normalize_phone)
    df["signup_date"] = df["signup_date"].apply(normalize_date)
    df["state"] = df["state"].apply(normalize_state)

    df["age"] = pd.to_numeric(df["age"], errors="coerce")
    df["salary"] = pd.to_numeric(df["salary"], errors="coerce")

    df = df[~((df["age"] < 0) | (df["age"] > 120))]
    df = df[~((df["salary"] < 0) | (df["salary"] > 1_000_000))]

    df["age"] = df["age"].apply(lambda x: str(int(x)) if pd.notna(x) else "")
    df["salary"] = df["salary"].apply(lambda x: str(int(x)) if pd.notna(x) else "")

    df = df[df["email"] != ""]
    df = df.drop_duplicates()
    df = df.drop_duplicates(subset=["name", "email"], keep="first")

    df.to_csv(output_path, index=False)


if __name__ == "__main__":
    clean()
