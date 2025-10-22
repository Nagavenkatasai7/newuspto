"""
Research Format Excel Exporter

Creates Excel output matching the research database format with:
- Fixed metadata columns (brand_id, gvkey, conm, Alt Name, Plaintiff, Marks, US GS, INT GS, dates, Result)
- Alternating TM Type, Serial Number columns

Format:
brand_id | gvkey | conm | Alt Name | Plaintiff | Marks | US GS | INT GS | Opp Start Date | Opp End Date | Result | TM Type | Serial No | TM Type | Serial No | ...
"""

import pandas as pd
import io
from typing import Dict, List
from openpyxl.styles import Font, Alignment, PatternFill


def create_research_format_excel(result: Dict, brand_id: str = "", gvkey: str = "") -> bytes:
    """
    Create Excel file in research database format.

    Format matches example.xlsx:
    - One row per opposition
    - Alternating TM Type and Serial Number columns after fixed metadata

    Args:
        result: Bulk scrape result from bulk_scrape_party_consolidated()
        brand_id: Optional brand identifier
        gvkey: Optional company identifier (GVKEY)

    Returns:
        bytes: Excel file content
    """
    output = io.BytesIO()

    rows = []
    max_marks = 0

    # First pass: determine maximum number of marks across all oppositions
    for opp in result.get('oppositions', []):
        serial_count = opp.get('serial_count', 0)
        if serial_count > max_marks:
            max_marks = serial_count

    # Build rows
    for opp in result.get('oppositions', []):
        # Skip failed oppositions
        if opp.get('status') == 'FAILED':
            continue

        # Fixed columns
        row = {
            'brand_id': brand_id,
            'gvkey': gvkey,
            'conm': result.get('party_name', ''),
            'Alt Name': result.get('party_name', ''),  # User can update this manually
            'Plaintiff': 1 if opp.get('plaintiff', '').lower() == result.get('party_name', '').lower() else 0,
            'Marks': opp.get('serial_count', 0),
            'US GS': len(opp.get('unique_us_classes', '').split(', ')) if opp.get('unique_us_classes') else 0,
            'INT GS': len(opp.get('unique_international_classes', '').split(', ')) if opp.get('unique_international_classes') else 0,
            'Opp Start Date': opp.get('filing_date', ''),
            'Opp End Date': opp.get('termination_date', ''),
            'Result': opp.get('result', ''),  # 0=Dismissed, 1=Sustained, None=Pending
        }

        # Parse serial numbers and mark types
        serial_numbers = opp.get('serial_numbers', '').split(', ') if opp.get('serial_numbers') else []
        mark_types_str = opp.get('mark_types', '').split(', ') if opp.get('mark_types') else []

        # Add alternating TM Type and Serial Number columns
        for i in range(max_marks):
            if i < len(serial_numbers):
                # Add TM Type
                tm_type = mark_types_str[i] if i < len(mark_types_str) else ''
                serial_no = serial_numbers[i] if i < len(serial_numbers) else ''

                if i == 0:
                    # First mark uses fixed column names
                    row['TM Type'] = tm_type
                    row['Serial No of Trademark'] = serial_no
                else:
                    # Subsequent marks use alternating unnamed columns
                    # Column pattern: TM Type (even), Serial (odd)
                    col_offset = (i - 1) * 2
                    row[f'_tm_type_{i}'] = tm_type
                    row[f'_serial_{i}'] = serial_no
            else:
                # Fill with empty values
                if i == 0:
                    row['TM Type'] = ''
                    row['Serial No of Trademark'] = ''
                else:
                    col_offset = (i - 1) * 2
                    row[f'_tm_type_{i}'] = ''
                    row[f'_serial_{i}'] = ''

        rows.append(row)

    if not rows:
        # No successful oppositions
        df = pd.DataFrame(columns=[
            'brand_id', 'gvkey', 'conm', 'Alt Name', 'Plaintiff', 'Marks',
            'US GS', 'INT GS', 'Opp Start Date', 'Opp End Date', 'Result',
            'TM Type', 'Serial No of Trademark'
        ])
    else:
        df = pd.DataFrame(rows)

        # Rename columns to match example format (unnamed columns)
        new_columns = {}
        for col in df.columns:
            if col.startswith('_tm_type_') or col.startswith('_serial_'):
                new_columns[col] = ''  # Make them unnamed (will show as Unnamed in Excel)

        if new_columns:
            df = df.rename(columns=new_columns)

    # Write to Excel
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Sheet1', index=False, header=True)

        # Format the sheet
        workbook = writer.book
        sheet = workbook['Sheet1']

        # Header styling (blue background, white text)
        header_fill = PatternFill(start_color='4472C4', end_color='4472C4', fill_type='solid')
        header_font = Font(bold=True, color='FFFFFF', size=11)

        for cell in sheet[1]:
            cell.fill = header_fill
            cell.font = header_font
            cell.alignment = Alignment(horizontal='center', vertical='center')

        # Auto-adjust column widths
        for column in sheet.columns:
            max_length = 0
            column_letter = column[0].column_letter
            for cell in column:
                try:
                    if cell.value and len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 25)  # Cap at 25
            sheet.column_dimensions[column_letter].width = adjusted_width

    return output.getvalue()


def create_copyable_research_format(result: Dict, brand_id: str = "", gvkey: str = "") -> str:
    """
    Create tab-separated text for direct copy-paste into existing Excel research file.

    Format: One row per opposition, tab-separated values
    Returns: String with \\t separators for Excel paste
    """
    rows = []
    max_marks = 0

    # Determine max marks
    for opp in result.get('oppositions', []):
        serial_count = opp.get('serial_count', 0)
        if serial_count > max_marks:
            max_marks = serial_count

    # Build rows
    for opp in result.get('oppositions', []):
        if opp.get('status') == 'FAILED':
            continue

        # Fixed columns
        row_values = [
            brand_id,
            gvkey,
            result.get('party_name', ''),
            result.get('party_name', ''),  # Alt Name
            '1' if opp.get('plaintiff', '').lower() == result.get('party_name', '').lower() else '0',
            str(opp.get('serial_count', 0)),
            str(len(opp.get('unique_us_classes', '').split(', ')) if opp.get('unique_us_classes') else 0),
            str(len(opp.get('unique_international_classes', '').split(', ')) if opp.get('unique_international_classes') else 0),
            str(opp.get('filing_date', '')),
            str(opp.get('termination_date', '')),
            str(opp.get('result', '') if opp.get('result') is not None else ''),
        ]

        # Parse serial numbers and mark types
        serial_numbers = opp.get('serial_numbers', '').split(', ') if opp.get('serial_numbers') else []
        mark_types_str = opp.get('mark_types', '').split(', ') if opp.get('mark_types') else []

        # Add alternating TM Type and Serial Number
        for i in range(max_marks):
            if i < len(serial_numbers):
                tm_type = mark_types_str[i] if i < len(mark_types_str) else ''
                serial_no = serial_numbers[i] if i < len(serial_numbers) else ''
                row_values.append(tm_type)
                row_values.append(serial_no)
            else:
                row_values.append('')
                row_values.append('')

        rows.append('\t'.join(row_values))

    return '\n'.join(rows)
