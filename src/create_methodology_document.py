#!/usr/bin/env python3
"""
Create a comprehensive methodology document explaining how the
US Territory mortality statistics were calculated.
"""

import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer,
    PageBreak, Preformatted
)
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from datetime import datetime

# Output path - relative to project root
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
OUTPUT_FILE = os.path.join(PROJECT_ROOT, "output", "Methodology_US_Territory_Mortality_Statistics.pdf")

def create_methodology_document():
    """Create the methodology PDF document."""

    doc = SimpleDocTemplate(
        OUTPUT_FILE,
        pagesize=letter,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch,
        leftMargin=0.6*inch,
        rightMargin=0.6*inch
    )

    elements = []
    styles = getSampleStyleSheet()

    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Title'],
        fontSize=20,
        spaceAfter=30,
        alignment=TA_CENTER,
    )

    heading1_style = ParagraphStyle(
        'Heading1Custom',
        parent=styles['Heading1'],
        fontSize=16,
        spaceBefore=20,
        spaceAfter=12,
        textColor=colors.HexColor('#2E8B57'),
    )

    heading2_style = ParagraphStyle(
        'Heading2Custom',
        parent=styles['Heading2'],
        fontSize=13,
        spaceBefore=15,
        spaceAfter=8,
        textColor=colors.HexColor('#444444'),
    )

    body_style = ParagraphStyle(
        'BodyCustom',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=8,
        alignment=TA_JUSTIFY,
        leading=14,
    )

    code_style = ParagraphStyle(
        'CodeCustom',
        parent=styles['Code'],
        fontSize=7.5,
        fontName='Courier',
        backColor=colors.HexColor('#F5F5F5'),
        borderColor=colors.HexColor('#CCCCCC'),
        borderWidth=1,
        borderPadding=5,
        leftIndent=10,
        rightIndent=10,
        spaceAfter=10,
        leading=9,
    )

    note_style = ParagraphStyle(
        'NoteCustom',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#666666'),
        leftIndent=20,
        rightIndent=20,
        spaceAfter=10,
        backColor=colors.HexColor('#FFFACD'),
        borderPadding=10,
    )

    # Table cell style for wrapping text
    cell_style = ParagraphStyle(
        'CellStyle',
        parent=styles['Normal'],
        fontSize=9,
        leading=11,
    )

    # Header cell style (white text for colored backgrounds)
    header_cell_style = ParagraphStyle(
        'HeaderCellStyle',
        parent=styles['Normal'],
        fontSize=9,
        leading=11,
        textColor=colors.white,
    )

    # =========================================================================
    # TITLE PAGE
    # =========================================================================
    elements.append(Spacer(1, 1.5*inch))
    elements.append(Paragraph("Methodology Document", title_style))
    elements.append(Paragraph("US Territory Mortality Statistics 2023",
                             ParagraphStyle('Subtitle', parent=styles['Heading2'],
                                          alignment=TA_CENTER, fontSize=14)))
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph("Drug-Related Deaths, Overdose Deaths, and Suicide Deaths<br/>for Guam, Puerto Rico, Virgin Islands, American Samoa,<br/>and Northern Mariana Islands",
                             ParagraphStyle('SubSubtitle', parent=body_style,
                                          alignment=TA_CENTER)))
    elements.append(Spacer(1, 1*inch))
    elements.append(Paragraph(f"Prepared: {datetime.now().strftime('%B %d, %Y')}",
                             ParagraphStyle('Date', parent=body_style, alignment=TA_CENTER)))
    elements.append(PageBreak())

    # =========================================================================
    # TABLE OF CONTENTS
    # =========================================================================
    elements.append(Paragraph("Table of Contents", heading1_style))
    toc_items = [
        "1. Overview and Request",
        "2. Data Source",
        "3. File Format and Layout",
        "4. Field Definitions",
        "5. ICD-10 Code Classifications",
        "6. Data Processing Code",
        "7. Results",
        "8. Appendix: Verification",
    ]
    for item in toc_items:
        elements.append(Paragraph(item, body_style))
    elements.append(PageBreak())

    # =========================================================================
    # SECTION 1: OVERVIEW
    # =========================================================================
    elements.append(Paragraph("1. Overview and Request", heading1_style))

    elements.append(Paragraph(
        "This document describes the methodology used to calculate mortality statistics "
        "for US territories using CDC Multiple Cause of Death Public Use Files. The analysis "
        "was performed to create fact sheets for the following US territories:",
        body_style
    ))

    territory_list = [
        "Guam (GU)",
        "Puerto Rico (PR)",
        "Virgin Islands (VI)",
        "American Samoa (AS)",
        "Northern Mariana Islands (MP)",
    ]
    for t in territory_list:
        elements.append(Paragraph(f"• {t}", ParagraphStyle('ListItem', parent=body_style, leftIndent=20)))

    elements.append(Spacer(1, 10))
    elements.append(Paragraph(
        "The requested statistics included: (1) Drug-related deaths, (2) Overdose-related deaths, "
        "and (3) Suicide deaths for the year 2023.",
        body_style
    ))

    # =========================================================================
    # SECTION 2: DATA SOURCE
    # =========================================================================
    elements.append(Paragraph("2. Data Source", heading1_style))

    elements.append(Paragraph(
        "The data was obtained from the CDC National Center for Health Statistics (NCHS) "
        "Multiple Cause of Death Public Use Files. These files contain mortality data "
        "collected from death certificates filed in the United States.",
        body_style
    ))

    elements.append(Paragraph("2.1 Download Location", heading2_style))
    elements.append(Paragraph(
        "The data was downloaded from the CDC FTP server:",
        body_style
    ))
    elements.append(Preformatted(
        "URL:  https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/DVS/mortality/\n"
        "File: mort2023ps.zip\n"
        "Unzipped file: VS23MORT.DPSMCPUB_r20241030",
        code_style
    ))

    elements.append(Paragraph(
        "<b>Note:</b> The CDC provides separate files for US states and US territories. "
        "The file used (mort2023ps.zip) contains data specifically for US possessions/territories.",
        note_style
    ))

    elements.append(Paragraph("2.2 File Characteristics", heading2_style))
    file_chars = [
        ["Characteristic", "Value"],
        ["Data Year", "2023"],
        ["File Format", "Fixed-width ASCII text"],
        ["Record Length", "818 characters per line"],
        ["Total Records (Territories)", "36,476"],
        ["Encoding", "Latin-1"],
    ]
    file_table = Table(file_chars, colWidths=[2.5*inch, 4.3*inch])
    file_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E8B57')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('BACKGROUND', (0, 1), (-1, -1), colors.white),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(file_table)

    elements.append(Paragraph("2.3 Documentation Reference", heading2_style))
    elements.append(Paragraph(
        "The file layout documentation was obtained from:",
        body_style
    ))
    elements.append(Preformatted(
        "URL: https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Dataset_Documentation/\n"
        "     DVS/mortality/2022-Mortality-Public-Use-File-Documentation.pdf\n\n"
        "Note: The 2022 documentation applies to the 2023 file format as well.",
        code_style
    ))

    elements.append(PageBreak())

    # =========================================================================
    # SECTION 3: FILE FORMAT
    # =========================================================================
    elements.append(Paragraph("3. File Format and Layout", heading1_style))

    elements.append(Paragraph(
        "The CDC mortality file uses a fixed-width format where each field occupies "
        "specific character positions. The following table shows the key fields used "
        "in this analysis:",
        body_style
    ))

    elements.append(Paragraph("3.1 Key Field Positions", heading2_style))

    # Use Paragraph objects for cells that need wrapping
    field_data = [
        [Paragraph("<b>Field Name</b>", header_cell_style),
         Paragraph("<b>Position</b>", header_cell_style),
         Paragraph("<b>Length</b>", header_cell_style),
         Paragraph("<b>Description</b>", header_cell_style)],
        [Paragraph("State of Occurrence", cell_style), "21-22", "2",
         Paragraph("FIPS state/territory code where death occurred", cell_style)],
        [Paragraph("State of Residence", cell_style), "29-30", "2",
         Paragraph("FIPS state/territory code of decedent's residence", cell_style)],
        ["Data Year", "102-105", "4", Paragraph("Year of death (e.g., 2023)", cell_style)],
        ["Manner of Death", "107", "1", Paragraph("Code indicating manner of death (1-7)", cell_style)],
        [Paragraph("ICD-10 Underlying Cause", cell_style), "146-149", "4",
         Paragraph("ICD-10 code for underlying cause of death", cell_style)],
    ]

    field_table = Table(field_data, colWidths=[1.6*inch, 0.8*inch, 0.6*inch, 3.8*inch])
    field_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E8B57')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('ALIGN', (1, 1), (2, -1), 'CENTER'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(field_table)

    elements.append(Spacer(1, 10))
    elements.append(Paragraph(
        "<b>Important:</b> Position numbers in the CDC documentation are 1-indexed. "
        "When using Python (0-indexed), subtract 1 from the starting position. "
        "For example, 'Position 21-22' in the documentation corresponds to "
        "<font face='Courier'>line[20:22]</font> in Python.",
        note_style
    ))

    elements.append(Paragraph("3.2 Sample Raw Data", heading2_style))
    elements.append(Paragraph(
        "Below is a sample record from the data file with key fields highlighted:",
        body_style
    ))
    elements.append(Preformatted(
        "Sample line (first 160 characters):\n"
        "                    11GU010  3GU  GU010             3               GU...\n"
        "                    ^^      ^^                                          \n"
        "                    ||      ||                                          \n"
        "Position:          21-22   29-30                                       \n"
        "Field:             State   State                                       \n"
        "                   Occur   Resid                                       \n"
        "Value:              GU      GU                                         ",
        code_style
    ))

    elements.append(PageBreak())

    # =========================================================================
    # SECTION 4: FIELD DEFINITIONS
    # =========================================================================
    elements.append(Paragraph("4. Field Definitions", heading1_style))

    elements.append(Paragraph("4.1 Territory Codes", heading2_style))
    elements.append(Paragraph(
        "US territories are identified using 2-character FIPS codes. Statistics were "
        "calculated based on <b>State of Occurrence</b> (position 21-22), meaning deaths "
        "are attributed to the territory where the death occurred. This matches the CDC VSRR "
        "(Vital Statistics Rapid Release) methodology.",
        body_style
    ))

    territory_codes = [
        ["Code", "Territory", "Records in 2023 File"],
        ["GU", "Guam", "1,193"],
        ["PR", "Puerto Rico", "34,290"],
        ["VI", "Virgin Islands", "758"],
        ["AS", "American Samoa", "0 (no data)"],
        ["MP", "Northern Mariana Islands", "235"],
    ]

    terr_table = Table(territory_codes, colWidths=[1*inch, 3*inch, 2.8*inch])
    terr_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E8B57')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, 0), 'LEFT'),   # Header row all left
        ('ALIGN', (0, 1), (-1, -1), 'LEFT'),  # Data rows left by default
        ('ALIGN', (2, 1), (2, -1), 'RIGHT'),  # Records column data right-aligned
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(terr_table)

    elements.append(Paragraph("4.2 Manner of Death Codes", heading2_style))
    elements.append(Paragraph(
        "The Manner of Death field (position 107) indicates how the death occurred:",
        body_style
    ))

    manner_codes = [
        ["Code", "Description"],
        ["1", "Accident"],
        ["2", "Suicide"],
        ["3", "Homicide"],
        ["4", "Pending investigation"],
        ["5", "Could not determine"],
        ["6", "Self-Inflicted"],
        ["7", "Natural"],
        ["Blank", "Not specified"],
    ]

    manner_table = Table(manner_codes, colWidths=[1*inch, 5.8*inch])
    manner_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E8B57')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
        ('TOPPADDING', (0, 0), (-1, -1), 5),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
    ]))
    elements.append(manner_table)

    elements.append(PageBreak())

    # =========================================================================
    # SECTION 5: ICD-10 CLASSIFICATIONS
    # =========================================================================
    elements.append(Paragraph("5. ICD-10 Code Classifications", heading1_style))

    elements.append(Paragraph(
        "The International Classification of Diseases, 10th Revision (ICD-10) codes "
        "are used to classify the underlying cause of death. The following sections "
        "describe how each statistic was defined using ICD-10 codes.",
        body_style
    ))

    elements.append(Paragraph("5.1 Drug Overdose Deaths", heading2_style))
    elements.append(Paragraph(
        "Drug overdose deaths are identified using ICD-10 codes for poisoning by drugs, "
        "medicaments, and biological substances. The following code ranges were used:",
        body_style
    ))

    overdose_codes = [
        [Paragraph("<b>ICD-10 Range</b>", header_cell_style),
         Paragraph("<b>Description</b>", header_cell_style),
         Paragraph("<b>Intent</b>", header_cell_style)],
        ["X40-X44",
         Paragraph("Accidental poisoning by drugs, medicaments and biological substances", cell_style),
         "Accidental"],
        ["X60-X64",
         Paragraph("Intentional self-poisoning by drugs, medicaments and biological substances", cell_style),
         Paragraph("Intentional (suicide)", cell_style)],
        ["Y10-Y14",
         Paragraph("Poisoning by drugs, medicaments and biological substances, undetermined intent", cell_style),
         "Undetermined"],
    ]

    od_table = Table(overdose_codes, colWidths=[1.1*inch, 4.2*inch, 1.5*inch])
    od_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E67E22')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#FFF5EE')]),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(od_table)

    elements.append(Paragraph("5.2 Drug-Related Deaths (Broader Definition)", heading2_style))
    elements.append(Paragraph(
        "Drug-related deaths include overdose deaths plus additional drug-induced causes. "
        "This broader category captures deaths where drugs played a significant role:",
        body_style
    ))

    drug_related_codes = [
        [Paragraph("<b>ICD-10 Range</b>", header_cell_style),
         Paragraph("<b>Description</b>", header_cell_style)],
        ["X40-X44, X60-X64, Y10-Y14",
         Paragraph("Drug overdose (as defined above)", cell_style)],
        ["F11-F16, F18-F19",
         Paragraph("Mental and behavioral disorders due to psychoactive substance use (excluding F10 alcohol and F17 tobacco)", cell_style)],
        ["T36-T50",
         Paragraph("Poisoning by drugs, medicaments and biological substances (therapeutic/accidental)", cell_style)],
    ]

    dr_table = Table(drug_related_codes, colWidths=[2.2*inch, 4.6*inch])
    dr_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E67E22')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#FFF5EE')]),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(dr_table)

    elements.append(Paragraph("5.3 Suicide Deaths", heading2_style))
    elements.append(Paragraph(
        "Suicide deaths are identified using two methods:",
        body_style
    ))
    elements.append(Paragraph(
        "<b>Method 1:</b> Manner of Death code = 2 (Suicide)<br/>"
        "<b>Method 2:</b> ICD-10 codes X60-X84 (Intentional self-harm) or U03 (Terrorism involving suicide)",
        body_style
    ))
    elements.append(Paragraph(
        "A death is counted as suicide if either condition is met.",
        body_style
    ))

    suicide_codes = [
        [Paragraph("<b>ICD-10 Range</b>", header_cell_style),
         Paragraph("<b>Description</b>", header_cell_style)],
        ["X60-X84",
         Paragraph("Intentional self-harm (includes all methods: poisoning, hanging, firearm, etc.)", cell_style)],
        ["U03", "Terrorism involving suicide"],
    ]

    sui_table = Table(suicide_codes, colWidths=[1.5*inch, 5.3*inch])
    sui_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498DB')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#EBF5FB')]),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(sui_table)

    elements.append(PageBreak())

    # =========================================================================
    # SECTION 6: DATA PROCESSING CODE
    # =========================================================================
    elements.append(Paragraph("6. Data Processing Code", heading1_style))

    elements.append(Paragraph(
        "The following Python code was used to process the CDC mortality data file. "
        "The code reads the fixed-width file, extracts relevant fields, and calculates "
        "statistics for each territory.",
        body_style
    ))

    elements.append(Paragraph("6.1 Reading the Data File", heading2_style))
    elements.append(Preformatted(
'''# Open and read the fixed-width data file
DATA_FILE = "VS23MORT.DPSMCPUB_r20241030"

with open(DATA_FILE, 'r', encoding='latin-1') as f:
    for line in f:
        if len(line) < 150:
            continue  # Skip malformed lines

        # Extract fields (0-indexed, documentation is 1-indexed)
        state_occurrence = line[20:22].strip()  # Position 21-22
        state_residence = line[28:30].strip()   # Position 29-30
        manner_of_death = line[106:107]         # Position 107
        icd10_code = line[145:149].strip()      # Position 146-149

        # Process record...''',
        code_style
    ))

    elements.append(Paragraph("6.2 Identifying Drug Overdose Deaths", heading2_style))
    elements.append(Preformatted(
'''def is_drug_overdose(icd10_code):
    """
    Check if ICD-10 code indicates drug overdose.
    Drug overdose codes:
    - X40-X44: Accidental poisoning by drugs
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

    return False''',
        code_style
    ))

    elements.append(Paragraph("6.3 Identifying Drug-Related Deaths", heading2_style))
    elements.append(Preformatted(
'''def is_drug_related(icd10_code):
    """
    Check if ICD-10 code indicates any drug-related death.
    Broader than overdose, includes:
    - Drug overdose (X40-X44, X60-X64, Y10-Y14)
    - Mental disorders due to drug use (F11-F16, F18-F19)
    - Drug toxicity and adverse effects (T36-T50)
    """
    code = icd10_code.strip().upper()
    if len(code) < 3:
        return False

    # Drug overdose codes
    if is_drug_overdose(icd10_code):
        return True

    # Mental/behavioral disorders from drugs (F11-F19, excluding F10, F17)
    if code.startswith('F1') and len(code) >= 3:
        digit = code[2]
        # Include F11-F16, F18-F19 (exclude F10=alcohol, F17=tobacco)
        if digit in '123456789' and digit != '0' and digit != '7':
            return True

    # Drug poisoning/toxicity codes (T36-T50)
    if code.startswith('T') and len(code) >= 3:
        try:
            num = int(code[1:3])
            if 36 <= num <= 50:
                return True
        except ValueError:
            pass

    return False''',
        code_style
    ))

    elements.append(PageBreak())

    elements.append(Paragraph("6.4 Identifying Suicide Deaths", heading2_style))
    elements.append(Preformatted(
'''def is_suicide(manner_code, icd10_code):
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

    return False''',
        code_style
    ))

    elements.append(Paragraph("6.5 Main Processing Loop", heading2_style))
    elements.append(Preformatted(
'''from collections import defaultdict

# Territory codes
TERRITORIES = {'GU': 'Guam', 'PR': 'Puerto Rico', 'VI': 'Virgin Islands',
               'AS': 'American Samoa', 'MP': 'Northern Mariana Islands'}

# Initialize statistics
stats = defaultdict(lambda: {
    'total_deaths': 0,
    'suicide_deaths': 0,
    'drug_overdose_deaths': 0,
    'drug_related_deaths': 0,
})

# Process each record
with open(DATA_FILE, 'r', encoding='latin-1') as f:
    for line in f:
        if len(line) < 150:
            continue

        # Use State of Occurrence (position 21-22) to match CDC VSRR methodology
        state_occurrence = line[20:22].strip()
        manner_of_death = line[106:107]
        icd10_code = line[145:149].strip()

        if state_occurrence not in TERRITORIES:
            continue

        stats[state_occurrence]['total_deaths'] += 1

        if is_suicide(manner_of_death, icd10_code):
            stats[state_occurrence]['suicide_deaths'] += 1

        if is_drug_overdose(icd10_code):
            stats[state_occurrence]['drug_overdose_deaths'] += 1

        if is_drug_related(icd10_code):
            stats[state_occurrence]['drug_related_deaths'] += 1''',
        code_style
    ))

    elements.append(PageBreak())

    # =========================================================================
    # SECTION 7: RESULTS
    # =========================================================================
    elements.append(Paragraph("7. Results", heading1_style))

    elements.append(Paragraph(
        "The following table presents the final mortality statistics for each US territory "
        "based on the 2023 CDC Multiple Cause of Death Public Use File:",
        body_style
    ))

    elements.append(Paragraph("7.1 Summary Statistics", heading2_style))

    results_data = [
        [Paragraph("<b>Territory</b>", header_cell_style),
         Paragraph("<b>Total Deaths</b>", header_cell_style),
         Paragraph("<b>Suicide Deaths</b>", header_cell_style),
         Paragraph("<b>Overdose Deaths</b>", header_cell_style),
         Paragraph("<b>Drug-Related Deaths</b>", header_cell_style)],
        ["Puerto Rico", "34,290", "236", "786", "2,412"],
        ["Guam", "1,193", "31", "34", "229"],
        ["Virgin Islands", "758", "10", "5", "23"],
        ["American Samoa", "N/A*", "N/A", "N/A", "N/A"],
        [Paragraph("Northern Mariana Islands", cell_style), "235", "4", "0", "25"],
    ]

    results_table = Table(results_data, colWidths=[1.8*inch, 1.1*inch, 1.1*inch, 1.2*inch, 1.6*inch])
    results_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E8B57')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, 0), 'LEFT'),  # Header row all left
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),   # Territory column left
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'), # Data values right
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elements.append(results_table)

    elements.append(Spacer(1, 10))
    elements.append(Paragraph(
        "*American Samoa: No mortality records were found in the 2023 CDC territories file. "
        "This may indicate that data was not reported or is reported through a different mechanism.",
        note_style
    ))

    elements.append(Paragraph("7.2 Validation: Public-Use Files vs CDC WONDER", heading2_style))
    elements.append(Paragraph(
        "The methodology matches the methodology that CDC WONDER uses. However, the public-use mortality "
        "files show 0.3-1.8% more deaths because: (1) CDC WONDER suppresses cells with &lt;10 deaths for "
        "privacy and excludes them from totals; (2) Downloadable files include late-filed death certificates "
        "not yet incorporated into WONDER; (3) Data release timing differences.",
        body_style
    ))
    elements.append(Spacer(1, 8))

    validation_data = [
        [Paragraph("<b>Year</b>", header_cell_style),
         Paragraph("<b>CDC WONDER</b>", header_cell_style),
         Paragraph("<b>Public-Use Files</b>", header_cell_style),
         Paragraph("<b>Difference</b>", header_cell_style)],
        ["2018", "72,444", "72,984", "+0.7%"],
        ["2019", "76,083", "76,655", "+0.8%"],
        ["2020", "97,841", "98,598", "+0.8%"],
        ["2021", "113,555", "114,488", "+0.8%"],
        ["2022", "114,652", "116,253", "+1.4%"],
        ["2023", "112,106", "114,121", "+1.8%"],
    ]

    validation_table = Table(validation_data, colWidths=[0.8*inch, 1.3*inch, 1.5*inch, 1*inch])
    validation_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E8B57')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    elements.append(validation_table)

    elements.append(PageBreak())

    # =========================================================================
    # SECTION 8: APPENDIX
    # =========================================================================
    elements.append(Paragraph("8. Appendix: Replication", heading1_style))

    elements.append(Paragraph(
        "The complete Python scripts used for data processing and fact sheet generation "
        "are included with this document:",
        body_style
    ))

    elements.append(Paragraph("• <b>process_mortality_data.py</b> - Main data processing script", body_style))
    elements.append(Paragraph("• <b>create_report.py</b> - PDF summary report generator", body_style))
    elements.append(Paragraph("• <b>create_methodology_document.py</b> - This methodology document generator", body_style))

    elements.append(Paragraph("8.1 Data Files", heading2_style))
    elements.append(Preformatted(
        "Data Files:\n"
        "  VS23MORT.DPSMCPUB_r20241030     (Raw mortality data from CDC)\n"
        "  2023-Mortality-Public-Use-File-Documentation.pdf (File layout documentation)\n\n"
        "Output:\n"
        "  territory_mortality_summary_2023.csv\n"
        "  US_Territory_Mortality_Statistics_2023.pdf\n"
        "  Methodology_US_Territory_Mortality_Statistics.pdf",
        code_style
    ))

    elements.append(Paragraph("8.2 Replication Steps", heading2_style))
    elements.append(Paragraph(
        "To verify these results, download the CDC mortality data file and run the processing script:",
        body_style
    ))
    elements.append(Preformatted(
        "# Download data from CDC\n"
        "wget https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/DVS/mortality/mort2023ps.zip\n"
        "unzip mort2023ps.zip\n\n"
        "# Run processing script\n"
        "python3 process_mortality_data.py",
        code_style
    ))

    elements.append(Spacer(1, 30))

    # Footer
    elements.append(Paragraph(
        f"<b>Date:</b> {datetime.now().strftime('%B %d, %Y')}<br/>"
        "<b>Data Source:</b> CDC NCHS Multiple Cause of Death Public Use Files, 2023",
        ParagraphStyle('Footer', parent=body_style, alignment=TA_CENTER, fontSize=9)
    ))

    # Build the document
    doc.build(elements)
    print(f"Methodology document created: {OUTPUT_FILE}")

if __name__ == "__main__":
    create_methodology_document()
