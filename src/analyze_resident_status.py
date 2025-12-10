#!/usr/bin/env python3
"""
Analyze mortality data excluding foreign residents to compare with CDC WONDER.

CDC WONDER may exclude foreign residents (resident_status = 4) from their counts.
This script tests that hypothesis by comparing counts with and without foreign residents.

Field: Position 20, Resident Status
  1 = Residents (state/county same for occurrence and residence)
  2 = Intrastate nonresidents (same state, different county)
  3 = Interstate nonresidents (different state, both in US)
  4 = Foreign residents (occurred in US, residence outside US)
"""

import os
import zipfile
import urllib.request
from collections import defaultdict

# Same ICD-10 codes as the main processing script
OVERDOSE_CODES = {
    "X40", "X41", "X42", "X43", "X44",  # Accidental poisoning
    "X60", "X61", "X62", "X63", "X64",  # Intentional self-poisoning
    "X85",                               # Assault by drugs
    "Y10", "Y11", "Y12", "Y13", "Y14",  # Undetermined intent
}

# Field positions (0-indexed)
RESIDENT_STATUS_POS = 19  # Position 20 in docs
UNDERLYING_CAUSE_START = 145
UNDERLYING_CAUSE_END = 149
RECORD_AXIS_START = 343
RECORD_AXIS_END = 443
STATE_OCCURRENCE_START = 20
STATE_OCCURRENCE_END = 22

# CDC data URLs
US_DATA_URL = "https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/DVS/mortality/mort2023us.zip"
US_DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")


def download_us_data():
    """Download US mortality data if not present."""
    import subprocess

    os.makedirs(US_DATA_DIR, exist_ok=True)
    zip_path = os.path.join(US_DATA_DIR, "mort2023us.zip")

    # Check if extracted file exists
    expected_files = ["VS23MORT.DUSMCPUB_r20241030", "VS23MORT.DUSMCPUB"]
    for f in expected_files:
        if os.path.exists(os.path.join(US_DATA_DIR, f)):
            return os.path.join(US_DATA_DIR, f)

    # Download if not exists
    if not os.path.exists(zip_path):
        print(f"Downloading US mortality data from {US_DATA_URL}...")
        urllib.request.urlretrieve(US_DATA_URL, zip_path)
        print("Download complete.")

    # Extract using system unzip (handles more compression methods)
    print("Extracting data...")
    subprocess.run(["unzip", "-o", zip_path, "-d", US_DATA_DIR], check=True)

    # Find extracted file
    for f in expected_files:
        if os.path.exists(os.path.join(US_DATA_DIR, f)):
            return os.path.join(US_DATA_DIR, f)

    raise FileNotFoundError("Could not find extracted US mortality data file")


def extract_icd_codes(record):
    """Extract all ICD-10 codes from a record (underlying + multiple cause)."""
    codes = []

    # Underlying cause (positions 146-149, 0-indexed: 145-148)
    underlying = record[UNDERLYING_CAUSE_START:UNDERLYING_CAUSE_END].strip()
    if underlying:
        codes.append(underlying)

    # Record-axis conditions (positions 344-443)
    # From CDC docs: Number of conditions at 341-342, conditions start at 344
    # Each condition is 5 positions (4 chars ICD + 1 blank)
    if len(record) >= 443:
        try:
            num_conditions = int(record[340:342].strip() or '0')
        except ValueError:
            num_conditions = 0

        for i in range(min(num_conditions, 20)):
            start = 343 + (i * 5)  # 0-indexed: position 344 = index 343
            end = start + 4
            if end <= len(record):
                code = record[start:end].strip()
                if code:
                    codes.append(code)

    return codes


def is_overdose_code(code):
    """Check if a single ICD-10 code indicates overdose."""
    code = code.strip().upper()
    if len(code) < 3:
        return False

    # Check X40-X44 (accidental drug poisoning)
    if code.startswith('X4') and len(code) >= 3:
        digit = code[2]
        if digit in '01234':
            return True

    # Check X60-X64 (intentional self-poisoning by drugs)
    if code.startswith('X6') and len(code) >= 3:
        digit = code[2]
        if digit in '01234':
            return True

    # Check X85 (assault/homicide by drugs)
    if code.startswith('X85'):
        return True

    # Check Y10-Y14 (undetermined intent drug poisoning)
    if code.startswith('Y1') and len(code) >= 3:
        digit = code[2]
        if digit in '01234':
            return True

    return False


def is_overdose(codes):
    """Check if any ICD codes indicate overdose."""
    for code in codes:
        if is_overdose_code(code):
            return True
    return False


def analyze_by_resident_status():
    """Analyze overdose deaths by resident status."""
    data_file = download_us_data()

    # Counters
    total_deaths = defaultdict(int)  # by resident status
    overdose_deaths = defaultdict(int)  # by resident status

    print(f"Processing {data_file}...")

    with open(data_file, 'r', encoding='latin-1') as f:
        for line_num, line in enumerate(f, 1):
            if len(line) < 400:
                continue

            # Get resident status (position 20, 0-indexed: 19)
            resident_status = line[RESIDENT_STATUS_POS] if len(line) > RESIDENT_STATUS_POS else ''

            # Only count US state deaths (not territories)
            state = line[STATE_OCCURRENCE_START:STATE_OCCURRENCE_END].strip()
            if state in ['GU', 'PR', 'VI', 'AS', 'MP']:
                continue

            total_deaths[resident_status] += 1

            # Check for overdose
            codes = extract_icd_codes(line)
            if is_overdose(codes):
                overdose_deaths[resident_status] += 1

            if line_num % 500000 == 0:
                print(f"  Processed {line_num:,} records...")

    return total_deaths, overdose_deaths


def main():
    print("=" * 70)
    print("Analysis: Mortality Data by Resident Status")
    print("Testing if CDC WONDER excludes foreign residents")
    print("=" * 70)
    print()

    total_deaths, overdose_deaths = analyze_by_resident_status()

    # Resident status labels
    status_labels = {
        '1': "Residents (same state/county)",
        '2': "Intrastate nonresidents (same state, diff county)",
        '3': "Interstate nonresidents (diff state, both US)",
        '4': "Foreign residents (occurred in US, lives abroad)",
        '': "Unknown/Missing",
    }

    print("\n" + "=" * 70)
    print("RESULTS: Total Deaths by Resident Status")
    print("=" * 70)

    grand_total = sum(total_deaths.values())
    for status in ['1', '2', '3', '4', '']:
        count = total_deaths.get(status, 0)
        pct = (count / grand_total * 100) if grand_total > 0 else 0
        label = status_labels.get(status, f"Status {status}")
        print(f"  {status or 'X'}: {count:>10,} ({pct:5.2f}%) - {label}")

    print(f"\n  TOTAL: {grand_total:>10,}")

    print("\n" + "=" * 70)
    print("RESULTS: Overdose Deaths by Resident Status")
    print("=" * 70)

    overdose_total = sum(overdose_deaths.values())
    for status in ['1', '2', '3', '4', '']:
        count = overdose_deaths.get(status, 0)
        pct = (count / overdose_total * 100) if overdose_total > 0 else 0
        label = status_labels.get(status, f"Status {status}")
        print(f"  {status or 'X'}: {count:>10,} ({pct:5.2f}%) - {label}")

    print(f"\n  TOTAL: {overdose_total:>10,}")

    # Calculate excluding foreign residents
    print("\n" + "=" * 70)
    print("COMPARISON WITH CDC WONDER (2023 Overdose Deaths)")
    print("=" * 70)

    cdc_wonder = 112106
    all_residents = overdose_total
    excluding_foreign = overdose_total - overdose_deaths.get('4', 0)

    print(f"\n  CDC WONDER:                    {cdc_wonder:>10,}")
    print(f"  Public-Use (ALL):              {all_residents:>10,} (+{(all_residents-cdc_wonder)/cdc_wonder*100:.2f}%)")
    print(f"  Public-Use (excl. foreign):    {excluding_foreign:>10,} (+{(excluding_foreign-cdc_wonder)/cdc_wonder*100:.2f}%)")
    print(f"\n  Foreign resident overdoses:    {overdose_deaths.get('4', 0):>10,}")

    # Total deaths comparison
    print("\n" + "=" * 70)
    print("COMPARISON: Total Deaths (2023)")
    print("=" * 70)

    cdc_wonder_total = 3090964
    all_total = grand_total
    excluding_foreign_total = grand_total - total_deaths.get('4', 0)

    print(f"\n  CDC WONDER/FastStats:          {cdc_wonder_total:>10,}")
    print(f"  Public-Use (ALL):              {all_total:>10,} (+{(all_total-cdc_wonder_total)/cdc_wonder_total*100:.2f}%)")
    print(f"  Public-Use (excl. foreign):    {excluding_foreign_total:>10,} (+{(excluding_foreign_total-cdc_wonder_total)/cdc_wonder_total*100:.2f}%)")
    print(f"\n  Foreign resident deaths:       {total_deaths.get('4', 0):>10,}")


if __name__ == "__main__":
    main()
