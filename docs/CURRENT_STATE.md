# Current State: US Territory Mortality Statistics

**Last Updated:** 2025-12-10

## Project Status: COMPLETE

The project extracts mortality statistics (drug-related deaths, overdose deaths, suicide deaths) for US territories from CDC public-use files. The methodology matches CDC WONDER exactly.

## What's Working

- ✅ Data extraction from CDC mortality public-use files
- ✅ Multiple cause of death analysis (underlying + contributing causes)
- ✅ Foreign resident exclusion to match CDC WONDER methodology
- ✅ PDF report generation
- ✅ Methodology document generation
- ✅ Validation against CDC WONDER (exact match for national data)
- ✅ All tables properly formatted (left-aligned, columns fit text)

## Key Files

| File | Purpose |
|------|---------|
| `src/process_mortality_data.py` | Main processing script - extracts territory statistics |
| `src/analyze_resident_status.py` | Validation script - confirms methodology matches WONDER |
| `src/create_report.py` | Generates summary PDF report |
| `src/create_methodology_document.py` | Generates detailed methodology PDF |
| `output/territory_mortality_summary_2023.csv` | Results in CSV format |
| `output/US_Territory_Mortality_Statistics_2023.pdf` | Summary report |
| `output/Methodology_US_Territory_Mortality_Statistics.pdf` | Full methodology |

## Data Files

| File | Location | Purpose |
|------|----------|---------|
| `VS23MORT.DPSMCPUB_r20241030` | `data/` | Territories mortality data (auto-downloaded) |
| `VS23MORT.DUSMCPUB_r20241030` | `data/` | US national mortality data (for validation) |
| `mort2023ps.zip` | CDC FTP | Source zip for territories |
| `mort2023us.zip` | CDC FTP | Source zip for national |

## Important Methodology Notes

### Foreign Resident Exclusion
Deaths with `resident_status = 4` (position 20 in data file) are excluded. These are deaths occurring in the US where the decedent resided outside the US. This matches CDC WONDER methodology.

### Validation Approach
CDC WONDER doesn't provide territory data. We validate by:
1. Running the same methodology on national US data
2. Comparing to CDC WONDER national counts
3. Achieving exact match confirms methodology is correct

### American Samoa
American Samoa did not report mortality data for 2023. See CDC NVSR Vol 74, No 8.

## Running the Scripts

```bash
# Process territory data (downloads if needed)
python3 src/process_mortality_data.py

# Generate PDFs
python3 src/create_report.py
python3 src/create_methodology_document.py

# Run national validation (downloads US data if needed)
python3 src/analyze_resident_status.py
```

## Current Results (2023, excluding foreign residents)

| Territory | Total Deaths | Drug-Related | Overdose | Suicide |
|-----------|-------------|--------------|----------|---------|
| Puerto Rico | 33,958 | 2,348 | 749 | 231 |
| Guam | 1,183 | 228 | 34 | 31 |
| Virgin Islands | 750 | 22 | 5 | 9 |
| American Samoa | N/A | N/A | N/A | N/A |
| N. Mariana Islands | 232 | 25 | 0 | 4 |

## Related Changelogs

- `.CHANGELOG/2025-12-10_163800_foreign-resident-analysis.md` - Initial discovery
- `.CHANGELOG/2025-12-10_164500_exclude-foreign-residents.md` - Implementation
- `.CHANGELOG/2025-12-10_170500_session-summary.md` - Full session summary

## No Known Issues

The project is complete and working as intended.
