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
    date_str = str(date_str).strip()
    from dateutil import parser
    try:
        dt = parser.parse(date_str, dayfirst=False)
        return dt.strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        pass
    # Try day-first
    try:
        dt = parser.parse(date_str, dayfirst=True)
        return dt.strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        return ""


def normalize_state(state):
    if pd.isna(state) or state == "":
        return ""
    s = str(state).strip().lower()
    if s in STATE_MAP:
        return STATE_MAP[s]
    # Already a 2-letter code
    if len(s) == 2 and s.upper() in STATE_MAP.values():
        return s.upper()
    return str(state).strip().upper()[:2]


def normalize_email(email):
    if pd.isna(email) or email == "":
        return ""
    e = str(email).strip().lower().replace(" ", "")
    if "@" not in e or "." not in e.split("@")[-1]:
        return ""
    return e


def clean(input_path="data/messy.csv", output_path="data/cleaned.csv"):
    df = pd.read_csv(input_path, dtype=str)

    # Strip whitespace from all columns
    for col in df.columns:
        df[col] = df[col].str.strip()

    # Replace sentinel null values
    null_values = ["N/A", "n/a", "null", "None", "none", "NULL", ""]
    for col in df.columns:
        df[col] = df[col].replace(null_values, "")

    # Normalize names to Title Case
    df["name"] = df["name"].apply(lambda x: x.title() if x else "")

    # Normalize emails
    df["email"] = df["email"].apply(normalize_email)

    # Normalize phones
    df["phone"] = df["phone"].apply(normalize_phone)

    # Normalize dates
    df["signup_date"] = df["signup_date"].apply(normalize_date)

    # Normalize states
    df["state"] = df["state"].apply(normalize_state)

    # Remove duplicates after normalization (before type conversion)
    df = df.drop_duplicates()

    # Convert age and salary to numeric, coerce errors
    df["age"] = pd.to_numeric(df["age"], errors="coerce")
    df["salary"] = pd.to_numeric(df["salary"], errors="coerce")

    # Remove outliers
    df = df[~((df["age"] < 0) | (df["age"] > 120))]
    df = df[~((df["salary"] < 0) | (df["salary"] > 1_000_000))]

    # Handle NaN from numeric conversion — convert back to empty string for output
    df["age"] = df["age"].apply(lambda x: str(int(x)) if pd.notna(x) else "")
    df["salary"] = df["salary"].apply(lambda x: str(int(x)) if pd.notna(x) else "")

    df.to_csv(output_path, index=False)


if __name__ == "__main__":
    clean()
