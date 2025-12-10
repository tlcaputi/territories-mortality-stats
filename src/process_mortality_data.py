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
    - X85: Assault by drugs, medicaments and biological substances (homicide by drugs)
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

    # Check X85 (assault/homicide by drugs)
    if code.startswith('X85'):
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
    Based on Connor Kubeisy's exact list from CDC NVSR 74-04 (pages 120-121).

    EXACT codes from Connor's email:
    D52.1, D59.0, D59.2, D61.1, D64.2, E06.4, E23.1, E24.2, E27.3, E66.1,
    F11.1-F11.5, F11.7-F11.9, F12.1-F12.5, F12.7-F12.9, F13.1-F13.5, F13.7-F13.9,
    F14.1-F14.5, F14.7-F14.9, F15.1-F15.5, F15.7-F15.9, F16.1-F16.5, F16.7-F16.9,
    F17.3-F17.5, F17.7-F17.9 (tobacco - note: NOT F17.1, F17.2),
    F18.1-F18.5, F18.7-F18.9, F19.1-F19.5, F19.7-F19.9,
    G21.1, G24.0, G25.1, G25.4, G25.6, G44.4, G62.0, G72.0, I95.2, J70.2, J70.3, J70.4,
    K85.3, L10.5, L27.0, L27.1, M10.2, M32.0, M80.4, M81.4, M83.5, M87.1, R50.2,
    R78.1, R78.2, R78.3, R78.4, R78.5, X40-X44, X60-X64, X85, Y10-Y14

    NOTE: Does NOT include T36-T50 (poisoning codes) per Connor's list.
    """
    code = icd10_code.strip().upper()
    if len(code) < 3:
        return False

    # Drug overdose codes (includes X85 for assault by drugs)
    if is_drug_overdose(icd10_code):
        return True

    # D codes - blood disorders: D52.1, D59.0, D59.2, D61.1, D64.2
    if code.startswith('D521') or code == 'D521':
        return True
    if code.startswith('D590') or code == 'D590':
        return True
    if code.startswith('D592') or code == 'D592':
        return True
    if code.startswith('D611') or code == 'D611':
        return True
    if code.startswith('D642') or code == 'D642':
        return True

    # E codes - endocrine disorders: E06.4, E23.1, E24.2, E27.3, E66.1
    if code.startswith('E064') or code == 'E064':
        return True
    if code.startswith('E231') or code == 'E231':
        return True
    if code.startswith('E242') or code == 'E242':
        return True
    if code.startswith('E273') or code == 'E273':
        return True
    if code.startswith('E661') or code == 'E661':
        return True

    # F codes - Mental and behavioral disorders due to psychoactive substance use
    # F11-F16, F18-F19: subcategories .1-.5, .7-.9 (NOT .0, .6)
    # F17 (tobacco): ONLY .3-.5, .7-.9 (NOT .0, .1, .2, .6)
    if code.startswith('F1') and len(code) >= 4:
        substance_digit = code[2]
        subcat = code[3]

        # F11-F16, F18-F19: .1-.5, .7-.9
        if substance_digit in '1234568' and substance_digit != '0':
            if subcat in '1234579':
                return True

        # F17 (tobacco): ONLY .3-.5, .7-.9
        if substance_digit == '7':
            if subcat in '34579':
                return True

        # F19: .1-.5, .7-.9
        if substance_digit == '9':
            if subcat in '1234579':
                return True

    # G codes - nervous system disorders: G21.1, G24.0, G25.1, G25.4, G25.6, G44.4, G62.0, G72.0
    if code.startswith('G211') or code == 'G211':
        return True
    if code.startswith('G240') or code == 'G240':
        return True
    if code.startswith('G251') or code == 'G251':
        return True
    if code.startswith('G254') or code == 'G254':
        return True
    if code.startswith('G256') or code == 'G256':
        return True
    if code.startswith('G444') or code == 'G444':
        return True
    if code.startswith('G620') or code == 'G620':
        return True
    if code.startswith('G720') or code == 'G720':
        return True

    # I codes - circulatory: I95.2
    if code.startswith('I952') or code == 'I952':
        return True

    # J codes - respiratory: J70.2, J70.3, J70.4
    if code.startswith('J702') or code == 'J702':
        return True
    if code.startswith('J703') or code == 'J703':
        return True
    if code.startswith('J704') or code == 'J704':
        return True

    # K codes - digestive: K85.3
    if code.startswith('K853') or code == 'K853':
        return True

    # L codes - skin: L10.5, L27.0, L27.1
    if code.startswith('L105') or code == 'L105':
        return True
    if code.startswith('L270') or code == 'L270':
        return True
    if code.startswith('L271') or code == 'L271':
        return True

    # M codes - musculoskeletal: M10.2, M32.0, M80.4, M81.4, M83.5, M87.1
    if code.startswith('M102') or code == 'M102':
        return True
    if code.startswith('M320') or code == 'M320':
        return True
    if code.startswith('M804') or code == 'M804':
        return True
    if code.startswith('M814') or code == 'M814':
        return True
    if code.startswith('M835') or code == 'M835':
        return True
    if code.startswith('M871') or code == 'M871':
        return True

    # R codes - symptoms/lab: R50.2, R78.1, R78.2, R78.3, R78.4, R78.5
    if code.startswith('R502') or code == 'R502':
        return True
    if code.startswith('R781') or code == 'R781':
        return True
    if code.startswith('R782') or code == 'R782':
        return True
    if code.startswith('R783') or code == 'R783':
        return True
    if code.startswith('R784') or code == 'R784':
        return True
    if code.startswith('R785') or code == 'R785':
        return True

    return False

def is_suicide_code(icd10_code):
    """
    Check if ICD-10 code indicates suicide.
    - X60-X84: Intentional self-harm
    - U03: Terrorism involving suicide
    - Y87.0: Sequelae of intentional self-harm
    """
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

    # Y87.0: Sequelae of intentional self-harm
    if code.startswith('Y870'):
        return True

    return False


def is_suicide(manner_code, icd10_code):
    """
    Check if death is suicide.
    - Manner of death = 2 (Suicide)
    - OR ICD-10 codes indicating suicide
    """
    # Check manner of death
    if manner_code == '2':
        return True

    # Check ICD-10 codes for suicide
    return is_suicide_code(icd10_code)


def extract_multiple_causes(line):
    """
    Extract all causes of death from record-axis conditions.

    From CDC documentation:
    - Number of record-axis conditions: positions 341-342
    - Record-axis conditions: positions 344-443 (up to 20 conditions)
    - Each condition: 5 positions (4 chars ICD code + 1 blank)

    Returns list of ICD-10 codes.
    """
    causes = []

    if len(line) < 443:
        return causes

    try:
        num_conditions = int(line[340:342].strip() or '0')
    except ValueError:
        num_conditions = 0

    # Extract each condition (max 20)
    for i in range(min(num_conditions, 20)):
        start = 343 + (i * 5)  # 0-indexed: position 344 = index 343
        end = start + 4
        if end <= len(line):
            code = line[start:end].strip()
            if code:
                causes.append(code)

    return causes


def check_any_cause(icd_codes, check_function):
    """
    Check if any of the ICD codes match the given check function.
    """
    for code in icd_codes:
        if check_function(code):
            return True
    return False


def process_mortality_data(use_multiple_causes=True):
    """
    Process the mortality data file and calculate statistics.

    Args:
        use_multiple_causes: If True, check both underlying and contributing causes.
                           If False, only check underlying cause (position 146-149).
    """

    stats = defaultdict(lambda: {
        'total_deaths': 0,
        'suicide_deaths': 0,
        'drug_overdose_deaths': 0,
        'drug_related_deaths': 0,
        'accidental_deaths': 0,
        'homicide_deaths': 0,
        'natural_deaths': 0,
        'icd10_codes': defaultdict(int),
        'multiple_cause_codes': defaultdict(int)
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
            underlying_cause = line[145:149].strip()  # Position 146-149 (underlying cause)

            # Use state of occurrence for statistics (matches CDC VSRR methodology)
            territory = state_occurrence

            if territory not in TERRITORIES:
                continue

            total_records += 1
            stats[territory]['total_deaths'] += 1

            # Track underlying cause ICD-10 code
            stats[territory]['icd10_codes'][underlying_cause] += 1

            # Get all causes (underlying + contributing) if enabled
            if use_multiple_causes:
                all_causes = extract_multiple_causes(line)
                # Always include underlying cause
                if underlying_cause and underlying_cause not in all_causes:
                    all_causes.insert(0, underlying_cause)

                # Track all multiple causes
                for code in all_causes:
                    stats[territory]['multiple_cause_codes'][code] += 1
            else:
                all_causes = [underlying_cause] if underlying_cause else []

            # Check for suicide (manner of death OR any cause code)
            is_suicide_death = manner_of_death == '2'
            if not is_suicide_death:
                is_suicide_death = check_any_cause(all_causes, is_suicide_code)
            if is_suicide_death:
                stats[territory]['suicide_deaths'] += 1

            # Check for drug overdose (any cause)
            if check_any_cause(all_causes, is_drug_overdose):
                stats[territory]['drug_overdose_deaths'] += 1

            # Check for drug-related (any cause, broader category)
            if check_any_cause(all_causes, is_drug_related):
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

def save_csv_output(stats, output_dir):
    """Save statistics to CSV files."""
    import csv

    os.makedirs(output_dir, exist_ok=True)

    # Summary CSV
    summary_file = os.path.join(output_dir, 'territory_mortality_summary_2023.csv')
    with open(summary_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([
            'Territory', 'Territory_Code', 'Total_Deaths',
            'Drug_Related_Deaths', 'Overdose_Related_Deaths', 'Suicide_Deaths',
            'Accidental_Deaths', 'Homicide_Deaths', 'Natural_Deaths'
        ])

        for territory_code in ['PR', 'GU', 'VI', 'AS', 'MP']:
            if territory_code in stats:
                data = stats[territory_code]
                name = TERRITORIES[territory_code]
                writer.writerow([
                    name, territory_code, data['total_deaths'],
                    data['drug_related_deaths'], data['drug_overdose_deaths'],
                    data['suicide_deaths'], data['accidental_deaths'],
                    data['homicide_deaths'], data['natural_deaths']
                ])
            else:
                name = TERRITORIES[territory_code]
                writer.writerow([name, territory_code, 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A', 'N/A'])

    print(f"Summary saved to: {summary_file}")

    # Detailed ICD-10 codes CSV
    codes_file = os.path.join(output_dir, 'territory_icd10_codes_2023.csv')
    with open(codes_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Territory', 'Territory_Code', 'ICD10_Code', 'Count', 'Is_Overdose', 'Is_Drug_Related', 'Is_Suicide'])

        for territory_code in ['PR', 'GU', 'VI', 'AS', 'MP']:
            if territory_code in stats:
                data = stats[territory_code]
                name = TERRITORIES[territory_code]
                for code, count in sorted(data['icd10_codes'].items(), key=lambda x: -x[1]):
                    if count > 0:
                        writer.writerow([
                            name, territory_code, code, count,
                            'Yes' if is_drug_overdose(code) else 'No',
                            'Yes' if is_drug_related(code) else 'No',
                            'Yes' if is_suicide_code(code) else 'No'
                        ])

    print(f"ICD-10 codes saved to: {codes_file}")


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

    # Save CSV output
    output_dir = os.path.join(PROJECT_ROOT, 'output')
    save_csv_output(stats, output_dir)
    print()
    print(f"Output files saved to: {output_dir}")
