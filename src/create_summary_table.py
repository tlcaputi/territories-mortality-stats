#!/usr/bin/env python3
"""
Create a single summary table with mortality statistics for all US Territories
"""

import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_LEFT

# Output path - relative to project root
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
OUTPUT_FILE = os.path.join(PROJECT_ROOT, "output", "US_Territory_Mortality_Statistics_2023.pdf")

def create_summary_table():
    """Create a single PDF with all territory statistics."""

    doc = SimpleDocTemplate(
        OUTPUT_FILE,
        pagesize=letter,
        topMargin=0.75*inch,
        bottomMargin=0.75*inch,
        leftMargin=0.75*inch,
        rightMargin=0.75*inch
    )

    elements = []
    styles = getSampleStyleSheet()

    # Title
    title_style = ParagraphStyle(
        'Title',
        parent=styles['Heading1'],
        fontSize=18,
        alignment=TA_CENTER,
        spaceAfter=20,
    )
    elements.append(Paragraph("US Territory Mortality Statistics, 2023", title_style))
    elements.append(Spacer(1, 20))

    # Main statistics table (based on State of Occurrence to match CDC VSRR methodology)
    data = [
        ["Territory", "Total Deaths", "Drug-Related Deaths", "Overdose Deaths", "Suicide Deaths"],
        ["Puerto Rico", "34,290", "825", "769", "236"],
        ["Guam", "1,193", "40", "30", "31"],
        ["Virgin Islands", "758", "5", "5", "10"],
        ["American Samoa", "N/A*", "N/A", "N/A", "N/A"],
        ["Northern Mariana Islands", "235", "0", "0", "4"],
    ]

    table = Table(data, colWidths=[2*inch, 1.1*inch, 1.5*inch, 1.4*inch, 1.2*inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2E8B57')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        # Header row: all left aligned
        ('ALIGN', (0, 0), (-1, 0), 'LEFT'),
        # Data rows: territory left, numbers right
        ('ALIGN', (0, 1), (0, -1), 'LEFT'),
        ('ALIGN', (1, 1), (-1, -1), 'RIGHT'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F5F5F5')]),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    elements.append(table)

    elements.append(Spacer(1, 15))

    # Footnote
    footnote_style = ParagraphStyle(
        'Footnote',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.gray,
    )
    elements.append(Paragraph("*American Samoa: No mortality records in 2023 CDC territories file.", footnote_style))

    elements.append(Spacer(1, 30))

    # Data source and definitions
    source_style = ParagraphStyle(
        'Source',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#444444'),
        spaceAfter=6,
    )

    elements.append(Paragraph("<b>Data Source:</b> CDC Multiple Cause of Death Public Use Files, 2023", source_style))
    elements.append(Paragraph("<b>Methodology:</b> Statistics based on State of Occurrence (where death occurred), matching CDC VSRR methodology.", source_style))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("<b>Definitions:</b>", source_style))
    elements.append(Paragraph("• <b>Drug-Related Deaths:</b> ICD-10 codes X40-X44, X60-X64, Y10-Y14, F11-F19, T36-T50", source_style))
    elements.append(Paragraph("• <b>Overdose Deaths:</b> ICD-10 codes X40-X44, X60-X64, Y10-Y14 (subset of drug-related)", source_style))
    elements.append(Paragraph("• <b>Suicide Deaths:</b> Manner of death = suicide, or ICD-10 codes X60-X84", source_style))

    doc.build(elements)
    print(f"Summary table created: {OUTPUT_FILE}")

if __name__ == "__main__":
    create_summary_table()
