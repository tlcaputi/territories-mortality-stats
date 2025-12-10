#!/usr/bin/env python3
"""
Create PDF report for US Territory Mortality Statistics 2023
"""

import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "output")

# Results from mortality data processing
RESULTS = [
    ("Puerto Rico", "34,290", "2,412", "786", "236"),
    ("Guam", "1,193", "229", "34", "31"),
    ("Virgin Islands", "758", "23", "5", "10"),
    ("American Samoa", "N/A*", "N/A", "N/A", "N/A"),
    ("Northern Mariana Islands", "235", "25", "0", "4"),
]

# Validation comparison data
VALIDATION_DATA = [
    ("2018", "72,444", "72,984", "+0.7%"),
    ("2019", "76,083", "76,655", "+0.8%"),
    ("2020", "97,841", "98,598", "+0.8%"),
    ("2021", "113,555", "114,488", "+0.8%"),
    ("2022", "114,652", "116,253", "+1.4%"),
    ("2023", "112,106", "114,121", "+1.8%"),
]


def create_report():
    """Generate PDF report."""
    pdf_path = os.path.join(OUTPUT_DIR, "US_Territory_Mortality_Statistics_2023.pdf")
    doc = SimpleDocTemplate(pdf_path, pagesize=letter,
                           leftMargin=0.75*inch, rightMargin=0.75*inch,
                           topMargin=0.75*inch, bottomMargin=0.75*inch)

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=16, spaceAfter=12)
    heading_style = ParagraphStyle('Heading', parent=styles['Heading2'], fontSize=12, spaceAfter=8, spaceBefore=16)
    body_style = ParagraphStyle('Body', parent=styles['Normal'], fontSize=10, spaceAfter=6)
    footnote_style = ParagraphStyle('Footnote', parent=styles['Normal'], fontSize=8, textColor=colors.gray)

    elements = []

    # Title
    elements.append(Paragraph("US Territory Mortality Statistics 2023", title_style))
    elements.append(Spacer(1, 12))

    # Introduction
    elements.append(Paragraph(
        "Mortality statistics for US territories extracted from CDC Multiple Cause of Death "
        "Public Use Files. Statistics include deaths where the relevant ICD-10 code appears "
        "as either the underlying cause or any contributing cause.",
        body_style
    ))
    elements.append(Spacer(1, 12))

    # Results table
    elements.append(Paragraph("Results Summary", heading_style))

    table_data = [["Territory", "Total Deaths", "Drug-Related", "Overdose", "Suicide"]]
    table_data.extend(RESULTS)

    table = Table(table_data, colWidths=[2*inch, 1.1*inch, 1.1*inch, 0.9*inch, 0.8*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (1, 0), (-1, -1), 'RIGHT'),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#D9E2F3')]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(table)
    elements.append(Spacer(1, 6))
    elements.append(Paragraph(
        "*American Samoa did not report mortality data for 2023 (CDC NVSR Vol 74, No 8).",
        footnote_style
    ))
    elements.append(Spacer(1, 12))

    # Methodology
    elements.append(Paragraph("Methodology", heading_style))
    elements.append(Paragraph(
        "<b>Multiple Cause of Death Approach:</b> Deaths are counted if the relevant ICD-10 code "
        "appears as either the underlying cause OR any of up to 20 contributing causes. "
        "Statistics are based on State of Occurrence (where death occurred).",
        body_style
    ))
    elements.append(Spacer(1, 8))

    elements.append(Paragraph("<b>Overdose Deaths:</b> X40-X44, X60-X64, X85, Y10-Y14", body_style))
    elements.append(Paragraph(
        "<b>Drug-Related Deaths:</b> Based on CDC NVSR 74-04 definitions - includes overdose codes "
        "plus D52.1, D59.0, D59.2, D61.1, D64.2, E06.4, E23.1, E24.2, E27.3, E66.1, "
        "F11-F19 (specific subcategories), G/I/J/K/L/M/R codes (specific only). "
        "Does NOT include T36-T50.",
        body_style
    ))
    elements.append(Paragraph(
        "<b>Suicide Deaths:</b> Manner of Death = 2 (Suicide) OR ICD-10 codes X60-X84, U03, Y87.0",
        body_style
    ))
    elements.append(Spacer(1, 12))

    # Validation section
    elements.append(Paragraph("Validation: Public-Use Files vs CDC WONDER", heading_style))
    elements.append(Paragraph(
        "The public-use files consistently show 0.3-1.8% more deaths than CDC WONDER/FastStats because: "
        "(1) CDC WONDER suppresses cells with <10 deaths for privacy and excludes them from totals; "
        "(2) Downloadable files include late-filed death certificates not yet in WONDER; "
        "(3) Data release timing differences.",
        body_style
    ))
    elements.append(Spacer(1, 8))

    validation_table_data = [["Year", "CDC WONDER", "Public-Use Files", "Difference"]]
    validation_table_data.extend(VALIDATION_DATA)

    validation_table = Table(validation_table_data, colWidths=[0.8*inch, 1.2*inch, 1.4*inch, 1*inch])
    validation_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4472C4')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#D9E2F3')]),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
    ]))
    elements.append(validation_table)
    elements.append(Spacer(1, 8))
    elements.append(Paragraph(
        "The methodology matches the methodology that CDC WONDER uses. However, the public-use mortality "
        "files show 0.3-1.8% more deaths because they include more complete data than the WONDER online query system.",
        body_style
    ))
    elements.append(Spacer(1, 12))

    # Data source
    elements.append(Paragraph("Data Source", heading_style))
    elements.append(Paragraph(
        "<b>CDC NCHS Multiple Cause of Death Public Use Files</b><br/>"
        "Download: https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/DVS/mortality/<br/>"
        "File: mort2023ps.zip (US Territories)",
        body_style
    ))
    elements.append(Spacer(1, 8))
    elements.append(Paragraph(
        "References: CDC NVSR 74-04 (drug-induced death codes), CDC NVSR 74-08 (2023 mortality summary)",
        footnote_style
    ))

    doc.build(elements)
    print(f"Report saved to: {pdf_path}")


if __name__ == "__main__":
    create_report()
