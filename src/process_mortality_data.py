#!/usr/bin/env python3
"""
Process CDC Mortality Data for US Territories
Extracts drug-related deaths, overdose deaths, and suicide deaths
"""

import os
import re
import urllib.request
import zipfile
from collections import defaultdict

# File paths - relative to project root
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
DATA_FILE = os.path.join(DATA_DIR, "VS23MORT.DPSMCPUB_r20241030")

# CDC data source
CDC_URL = "https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/DVS/mortality/mort2023ps.zip"
ZIP_FILE = os.path.join(DATA_DIR, "mort2023ps.zip")


def download_data():
    """Download and extract CDC mortality data if not present."""
    if os.path.exists(DATA_FILE):
        print(f"Data file already exists: {DATA_FILE}")
        return True

    os.makedirs(DATA_DIR, exist_ok=True)

    # Download zip file
    if not os.path.exists(ZIP_FILE):
        print(f"Downloading CDC mortality data from {CDC_URL}...")
        print("This may take a few minutes (~30MB)...")
        try:
            urllib.request.urlretrieve(CDC_URL, ZIP_FILE)
            print("Download complete.")
        except Exception as e:
            print(f"Error downloading data: {e}")
            return False

    # Extract zip file
    print("Extracting data...")
    try:
        with zipfile.ZipFile(ZIP_FILE, 'r') as zip_ref:
            zip_ref.extractall(DATA_DIR)
        print("Extraction complete.")

        # Clean up zip file
        os.remove(ZIP_FILE)
        return True
    except Exception as e:
        print(f"Error extracting data: {e}")
        return False

# Territory FIPS codes
TERRITORIES = {
    'GU': 'Guam',
    'PR': 'Puerto Rico',
    'VI': 'Virgin Islands',
    'AS': 'American Samoa',
    'MP': 'Northern Mariana Islands'
}

# Manner of Death codes
MANNER_OF_DEATH = {
    '1': 'Accident',
    '2': 'Suicide',
    '3': 'Homicide',
    '4': 'Pending investigation',
    '5': 'Could not determine',
    '6': 'Self-Inflicted',
    '7': 'Natural',
    ' ': 'Not specified'
}

def is_drug_overdose(icd10_code):
    """
    Check if ICD-10 code indicates drug overdose.
    Drug overdose codes:
    - X40-X44: Accidental poisoning by drugs, medicaments and biological substances
    - X60-X64: Intentional self-poisoning by drugs
    - Y10-Y14: Poisoning by drugs, undetermined intent
    """
    code = icd10_code.strip().upper()
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

    # Check Y10-Y14 (undetermined intent drug poisoning)
    if code.startswith('Y1') and len(code) >= 3:
        digit = code[2]
        if digit in '01234':
            return True

    return False

def is_drug_related(icd10_code):
    """
    Check if ICD-10 code indicates any drug-related death.
    This is broader than overdose and includes:
    - Drug overdose (X40-X44, X60-X64, Y10-Y14)
    - Drug-induced causes (F11-F16, F18-F19: Mental disorders due to drug use)
    - Drug toxicity and adverse effects
    """
    code = icd10_code.strip().upper()
    if len(code) < 3:
        return False

    # Drug overdose codes
    if is_drug_overdose(icd10_code):
        return True

    # Mental and behavioral disorders due to psychoactive substance use
    # F10 = Alcohol (not drug), F11-F16, F18-F19 = drugs
    if code.startswith('F1') and len(code) >= 3:
        digit = code[2]
        if digit in '123456789' and digit != '0' and digit != '7':  # Exclude F10 (alcohol) and F17 (tobacco)
            return True

    # Drug poisoning/toxicity codes
    # T36-T50: Poisoning by drugs, medicaments and biological substances
    if code.startswith('T') and len(code) >= 3:
        try:
            num = int(code[1:3])
            if 36 <= num <= 50:
                return True
        except ValueError:
            pass

    return False

def is_suicide(manner_code, icd10_code):
    """
    Check if death is suicide.
    - Manner of death = 2 (Suicide)
    - OR ICD-10 codes X60-X84 (Intentional self-harm)
    - OR ICD-10 code U03 (Terrorism involving suicide)
    """
    # Check manner of death
    if manner_code == '2':
        return True

    # Check ICD-10 codes for intentional self-harm
    code = icd10_code.strip().upper()
    if len(code) < 3:
        return False

    # X60-X84: Intentional self-harm
    if code.startswith('X'):
        try:
            num = int(code[1:3])
            if 60 <= num <= 84:
                return True
        except ValueError:
            pass

    # U03: Terrorism involving suicide
    if code.startswith('U03'):
        return True

    return False

def process_mortality_data():
    """Process the mortality data file and calculate statistics."""

    stats = defaultdict(lambda: {
        'total_deaths': 0,
        'suicide_deaths': 0,
        'drug_overdose_deaths': 0,
        'drug_related_deaths': 0,
        'accidental_deaths': 0,
        'homicide_deaths': 0,
        'natural_deaths': 0,
        'icd10_codes': defaultdict(int)
    })

    total_records = 0

    with open(DATA_FILE, 'r', encoding='latin-1') as f:
        for line in f:
            if len(line) < 150:
                continue

            # Extract fields (0-indexed, positions from documentation are 1-indexed)
            state_occurrence = line[20:22].strip()  # Position 21-22
            state_residence = line[28:30].strip()   # Position 29-30
            manner_of_death = line[106:107]         # Position 107
            icd10_code = line[145:149].strip()      # Position 146-149

            # Use state of occurrence for statistics (matches CDC VSRR methodology)
            territory = state_occurrence

            if territory not in TERRITORIES:
                continue

            total_records += 1
            stats[territory]['total_deaths'] += 1

            # Track ICD-10 codes
            stats[territory]['icd10_codes'][icd10_code] += 1

            # Check for suicide
            if is_suicide(manner_of_death, icd10_code):
                stats[territory]['suicide_deaths'] += 1

            # Check for drug overdose
            if is_drug_overdose(icd10_code):
                stats[territory]['drug_overdose_deaths'] += 1

            # Check for drug-related (broader category)
            if is_drug_related(icd10_code):
                stats[territory]['drug_related_deaths'] += 1

            # Track manner of death
            if manner_of_death == '1':
                stats[territory]['accidental_deaths'] += 1
            elif manner_of_death == '3':
                stats[territory]['homicide_deaths'] += 1
            elif manner_of_death == '7':
                stats[territory]['natural_deaths'] += 1

    return stats, total_records

def print_statistics(stats, total_records):
    """Print the mortality statistics."""

    print("=" * 70)
    print("CDC MORTALITY DATA 2023 - US TERRITORIES")
    print("=" * 70)
    print(f"\nTotal records processed: {total_records:,}")
    print()

    for territory_code in ['PR', 'GU', 'VI', 'AS', 'MP']:
        if territory_code not in stats:
            print(f"\n{TERRITORIES[territory_code]}: No data found")
            continue

        data = stats[territory_code]
        territory_name = TERRITORIES[territory_code]

        print("-" * 70)
        print(f"{territory_name} ({territory_code})")
        print("-" * 70)
        print(f"  Total Deaths:         {data['total_deaths']:,}")
        print(f"  Suicide Deaths:       {data['suicide_deaths']:,}")
        print(f"  Drug Overdose Deaths: {data['drug_overdose_deaths']:,}")
        print(f"  Drug-Related Deaths:  {data['drug_related_deaths']:,}")
        print(f"  Accidental Deaths:    {data['accidental_deaths']:,}")
        print(f"  Homicide Deaths:      {data['homicide_deaths']:,}")
        print(f"  Natural Deaths:       {data['natural_deaths']:,}")

        # Show top ICD-10 codes for drug-related deaths
        drug_codes = {}
        for code, count in data['icd10_codes'].items():
            if is_drug_related(code) or is_drug_overdose(code):
                drug_codes[code] = count

        if drug_codes:
            print(f"\n  Drug-Related ICD-10 Codes:")
            for code, count in sorted(drug_codes.items(), key=lambda x: -x[1])[:10]:
                print(f"    {code}: {count}")
        print()

    print("=" * 70)
    print("SUMMARY TABLE")
    print("=" * 70)
    print(f"{'Territory':<25} {'Total':>10} {'Suicide':>10} {'Overdose':>10} {'Drug-Rel':>10}")
    print("-" * 70)

    for territory_code in ['PR', 'GU', 'VI', 'AS', 'MP']:
        if territory_code in stats:
            data = stats[territory_code]
            name = TERRITORIES[territory_code]
            print(f"{name:<25} {data['total_deaths']:>10,} {data['suicide_deaths']:>10,} {data['drug_overdose_deaths']:>10,} {data['drug_related_deaths']:>10,}")
        else:
            name = TERRITORIES[territory_code]
            print(f"{name:<25} {'N/A':>10} {'N/A':>10} {'N/A':>10} {'N/A':>10}")

if __name__ == "__main__":
    print("Processing CDC mortality data for US territories...")
    print()

    # Download data if not present
    if not download_data():
        print("Failed to obtain data. Exiting.")
        exit(1)

    print()
    stats, total_records = process_mortality_data()
    print_statistics(stats, total_records)
