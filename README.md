# US Territory Mortality Statistics 2023

Mortality statistics (drug-related deaths, overdose deaths, and suicide deaths) for US territories extracted from CDC Multiple Cause of Death Public Use Files.

## Results Summary

| Territory | Total Deaths | Drug-Related Deaths | Overdose Deaths | Suicide Deaths |
|-----------|-------------|---------------------|-----------------|----------------|
| Puerto Rico | 34,290 | 825 | 769 | 236 |
| Guam | 1,193 | 40 | 30 | 31 |
| Virgin Islands | 758 | 5 | 5 | 10 |
| American Samoa | N/A* | N/A | N/A | N/A |
| Northern Mariana Islands | 235 | 0 | 0 | 4 |

\*American Samoa did not report mortality data for 2023 (see [CDC NVSR Vol 74, No 8](https://www.cdc.gov/nchs/data/nvsr/nvsr74/nvsr-74-08.pdf)).

### Methodology Note

Statistics are based on **State of Occurrence** (where death occurred), not State of Residence (where decedent lived). This matches the CDC VSRR (Vital Statistics Rapid Release) methodology.

**Validation:** Puerto Rico overdose deaths (769) matches CDC VSRR provisional data exactly.

## Project Structure

```
territories-mortality-stats/
├── README.md
├── requirements.txt
├── .gitignore
├── data/                    # CDC mortality data (auto-downloaded)
│   └── VS23MORT.DPSMCPUB_r20241030
├── src/                     # Python scripts
│   ├── process_mortality_data.py
│   ├── create_summary_table.py
│   └── create_methodology_document.py
└── output/                  # Generated PDFs
    ├── US_Territory_Mortality_Statistics_2023.pdf
    └── Methodology_US_Territory_Mortality_Statistics.pdf
```

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/tlcaputi/territories-mortality-stats.git
cd territories-mortality-stats

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run the data processing script (auto-downloads CDC data if needed)
python3 src/process_mortality_data.py

# 4. Generate PDF outputs (optional)
python3 src/create_summary_table.py
python3 src/create_methodology_document.py
```

The script automatically downloads the CDC mortality data (~30MB) on first run if not present.

**Note:** The main processing script (`process_mortality_data.py`) uses only Python standard library - no pip install needed to run it. `reportlab` is only required for PDF generation.

## Data Source

**CDC National Center for Health Statistics (NCHS) Multiple Cause of Death Public Use Files**

| Item | Value |
|------|-------|
| Download URL | https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/DVS/mortality/ |
| File | `mort2023ps.zip` (US territories/possessions) |
| Unzipped file | `VS23MORT.DPSMCPUB_r20241030` |
| Documentation | https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Dataset_Documentation/DVS/mortality/ |

The CDC provides separate files for US states and US territories. The file `mort2023ps.zip` contains mortality data specifically for US possessions/territories.

## File Format

The CDC mortality data is a **fixed-width ASCII text file**. Key fields:

| Field | Position | Length | Description |
|-------|----------|--------|-------------|
| State of Occurrence | 21-22 | 2 | FIPS code where death occurred |
| State of Residence | 29-30 | 2 | FIPS code of decedent's residence |
| Manner of Death | 107 | 1 | Code indicating manner (1-7) |
| ICD-10 Underlying Cause | 146-149 | 4 | ICD-10 cause of death code |

**Note:** Position numbers in CDC documentation are 1-indexed. In Python (0-indexed), subtract 1. For example, "Position 21-22" becomes `line[20:22]`.

**Important:** This project uses **State of Occurrence** (position 21-22) to match CDC VSRR methodology.

### Territory FIPS Codes

| Code | Territory |
|------|-----------|
| GU | Guam |
| PR | Puerto Rico |
| VI | Virgin Islands |
| AS | American Samoa |
| MP | Northern Mariana Islands |

### Manner of Death Codes

| Code | Description |
|------|-------------|
| 1 | Accident |
| 2 | Suicide |
| 3 | Homicide |
| 7 | Natural |

## ICD-10 Code Classifications

### Drug Overdose Deaths

| ICD-10 Range | Description | Intent |
|--------------|-------------|--------|
| X40-X44 | Accidental poisoning by drugs | Accidental |
| X60-X64 | Intentional self-poisoning by drugs | Intentional |
| Y10-Y14 | Poisoning by drugs, undetermined intent | Undetermined |

### Drug-Related Deaths (Broader Definition)

| ICD-10 Range | Description |
|--------------|-------------|
| X40-X44, X60-X64, Y10-Y14 | Drug overdose |
| F11-F16, F18-F19 | Mental/behavioral disorders due to substance use |
| T36-T50 | Poisoning by drugs and biological substances |

### Suicide Deaths

A death is counted as suicide if **either** condition is met:
1. Manner of Death code = 2 (Suicide)
2. ICD-10 codes X60-X84 (Intentional self-harm) or U03

## Code Overview

### Reading the Data

```python
with open(DATA_FILE, 'r', encoding='latin-1') as f:
    for line in f:
        state_occurrence = line[20:22].strip()  # Position 21-22 (where death occurred)
        state_residence = line[28:30].strip()   # Position 29-30 (where decedent lived)
        manner_of_death = line[106:107]         # Position 107
        icd10_code = line[145:149].strip()      # Position 146-149

        # Use state of occurrence to match CDC VSRR methodology
        territory = state_occurrence
```

### Classification Functions

```python
def is_drug_overdose(icd10_code):
    """X40-X44, X60-X64, Y10-Y14"""
    code = icd10_code.strip().upper()
    if code.startswith('X4') and code[2] in '01234': return True
    if code.startswith('X6') and code[2] in '01234': return True
    if code.startswith('Y1') and code[2] in '01234': return True
    return False

def is_suicide(manner_code, icd10_code):
    """Manner=2 or ICD-10 X60-X84"""
    if manner_code == '2': return True
    code = icd10_code.strip().upper()
    if code.startswith('X'):
        num = int(code[1:3])
        if 60 <= num <= 84: return True
    return False
```

## Notes

- Statistics use **State of Occurrence** (position 21-22), attributing deaths to where they occurred. This matches CDC VSRR methodology.
- **American Samoa** did not report mortality data for 2020-2023 per [CDC NVSR reports](https://www.cdc.gov/nchs/data/nvsr/nvsr74/nvsr-74-08.pdf).
- The 2022 CDC file format documentation applies to 2023 data.

## References

- CDC NCHS Multiple Cause of Death Files: https://www.cdc.gov/nchs/nvss/mortality_public_use_data.htm
- CDC National Vital Statistics Reports: https://www.cdc.gov/nchs/products/nvsr.htm
- ICD-10 Code Reference: https://www.cdc.gov/nchs/icd/icd10cm.htm

## License

Code provided for research and educational purposes. CDC mortality data is public domain.
