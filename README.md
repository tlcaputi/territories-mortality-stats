# US Territory Mortality Statistics 2023

Mortality statistics (drug-related deaths, overdose deaths, and suicide deaths) for US territories extracted from CDC Multiple Cause of Death Public Use Files.

## Results Summary

| Territory | Total Deaths | Drug-Related Deaths | Overdose Deaths | Suicide Deaths |
|-----------|-------------|---------------------|-----------------|----------------|
| Puerto Rico | 34,290 | 2,412 | 786 | 236 |
| Guam | 1,193 | 229 | 34 | 31 |
| Virgin Islands | 758 | 23 | 5 | 10 |
| American Samoa | N/A* | N/A | N/A | N/A |
| Northern Mariana Islands | 235 | 25 | 0 | 4 |

\*American Samoa did not report mortality data for 2023 (see [CDC NVSR Vol 74, No 8](https://www.cdc.gov/nchs/data/nvsr/nvsr74/nvsr-74-08.pdf)).

### Methodology Note

**Multiple Cause of Death Approach**: Statistics include deaths where the relevant ICD-10 code appears as either the underlying cause OR any contributing cause. This matches CDC WONDER "Multiple Cause of Death" methodology and captures all deaths related to the condition, not just those where it was the primary cause.

Statistics are based on **State of Occurrence** (where death occurred), not State of Residence.

## Validation: Public-Use Files vs CDC WONDER

This project uses **CDC NCHS Multiple Cause of Death Public-Use Files** (downloadable fixed-width data files). These differ slightly from **CDC WONDER** (the online query system) and **CDC FastStats** (which sources from WONDER).

### National Overdose Deaths Comparison

To validate our methodology, we compared **national US overdose death counts** from both data sources using identical ICD-10 codes (X40-X44, X60-X64, X85, Y10-Y14) as either underlying or contributing cause:

| Year | CDC WONDER | Public-Use Files | Difference |
|------|------------|------------------|------------|
| 2018 | 72,444 | 72,984 | +0.7% |
| 2019 | 76,083 | 76,655 | +0.8% |
| 2020 | 97,841 | 98,598 | +0.8% |
| 2021 | 113,555 | 114,488 | +0.8% |
| 2022 | 114,652 | 116,253 | +1.4% |
| 2023 | 112,106 | 114,121 | +1.8% |

### Total Deaths Comparison (2023)

| Source | Total Deaths |
|--------|-------------|
| CDC FastStats | 3,090,964 |
| CDC WONDER | 3,090,964 |
| Public-Use Files | 3,101,016 (+0.3%) |

### Why the Difference?

The public-use files consistently show 0.3-1.8% more deaths than WONDER/FastStats because:

1. **Cell suppression**: CDC WONDER suppresses cells with <10 deaths for privacy and excludes them from totals
2. **Late-filed certificates**: Downloadable files include late-filed death certificates not yet incorporated into WONDER
3. **Data release timing**: The 2023 file (October 2024 release) includes ~900 late-filed NC certificates that WONDER explicitly notes are excluded

**The methodology matches the methodology that CDC WONDER uses.** However, the public-use mortality files show 0.3-1.8% more deaths because they include more complete data than the WONDER online query system

## Definitions

### Overdose-Related Deaths
Deaths with **any of these ICD-10 codes** as underlying OR contributing cause:
- X40-X44: Accidental poisoning by drugs
- X60-X64: Intentional self-poisoning by drugs
- X85: Assault by drugs (homicide by poisoning)
- Y10-Y14: Poisoning by drugs, undetermined intent

### Drug-Related Deaths
Deaths with **any drug-induced ICD-10 code** as underlying OR contributing cause. Based on CDC NVSR 74-04 definitions (pages 120-121):
- All overdose codes (above)
- D52.1, D59.0, D59.2, D61.1, D64.2: Drug-induced blood disorders
- E06.4, E23.1, E24.2, E27.3, E66.1: Drug-induced endocrine disorders
- F11-F16, F18-F19 (subcategories .1-.5, .7-.9): Mental/behavioral disorders due to drugs
- F17.3-F17.5, F17.7-F17.9: Tobacco-related disorders (specific subcategories only)
- G21.1, G24.0, G25.1, G25.4, G25.6, G44.4, G62.0, G72.0: Drug-induced neurological disorders
- I95.2: Drug-induced hypotension
- J70.2-J70.4: Drug-induced respiratory disorders
- K85.3: Drug-induced pancreatitis
- L10.5, L27.0, L27.1: Drug-induced skin disorders
- M10.2, M32.0, M80.4, M81.4, M83.5, M87.1: Drug-induced musculoskeletal disorders
- R50.2, R78.1-R78.5: Drug-related symptoms and lab findings

**Note:** Does NOT include T36-T50 (poisoning codes) per the methodology used in CDC state factsheets.

### Suicide Deaths
Deaths where **either** condition is met:
1. Manner of Death = 2 (Suicide)
2. Any of these ICD-10 codes as underlying OR contributing cause:
   - X60-X84: Intentional self-harm
   - U03: Terrorism involving suicide
   - Y87.0: Sequelae of intentional self-harm

## Project Structure

```
territories-mortality-stats/
├── README.md
├── requirements.txt
├── .gitignore
├── data/                    # CDC mortality data (auto-downloaded)
│   └── VS23MORT.DPSMCPUB_r20241030
├── src/
│   ├── process_mortality_data.py       # Main data processing
│   ├── create_report.py                # Generate summary PDF
│   └── create_methodology_document.py  # Generate methodology PDF
└── output/
    ├── territory_mortality_summary_2023.csv
    ├── US_Territory_Mortality_Statistics_2023.pdf
    └── Methodology_US_Territory_Mortality_Statistics.pdf
```

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/tlcaputi/territories-mortality-stats.git
cd territories-mortality-stats

# 2. Run the data processing script (auto-downloads CDC data if needed)
python3 src/process_mortality_data.py
```

The script automatically downloads the CDC mortality data (~30MB) on first run if not present.

**Note:** Uses only Python standard library - no pip install needed.

## Data Source

**CDC National Center for Health Statistics (NCHS) Multiple Cause of Death Public Use Files**

| Item | Value |
|------|-------|
| Download URL | https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/DVS/mortality/ |
| Territories File | `mort2023ps.zip` |
| US States File | `mort2023us.zip` |
| Documentation | https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Dataset_Documentation/DVS/mortality/ |

## File Format

The CDC mortality data is a **fixed-width ASCII text file**. Key fields:

| Field | Position | Length | Description |
|-------|----------|--------|-------------|
| State of Occurrence | 21-22 | 2 | Territory code (PR, GU, VI, etc.) |
| Manner of Death | 107 | 1 | Code indicating manner (1-7) |
| ICD-10 Underlying Cause | 146-149 | 4 | Primary cause of death |
| Record-Axis Conditions | 341-443 | - | Up to 20 contributing causes |

### Territory Codes

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

## References

- CDC NCHS Multiple Cause of Death Files: https://www.cdc.gov/nchs/nvss/mortality_public_use_data.htm
- CDC NVSR 74-04 Drug-Induced Death Codes: https://www.cdc.gov/nchs/data/nvsr/nvsr74/nvsr74-04.pdf
- CDC National Vital Statistics Reports: https://www.cdc.gov/nchs/products/nvsr.htm
- ICD-10 Code Reference: https://www.cdc.gov/nchs/icd/icd10cm.htm
- Center for Drug Control Policy: https://drugcontrolpolicy.org/

## License

Code provided for research and educational purposes. CDC mortality data is public domain.
