"""
Bulk Copyable Format Exporter
Creates the same tab-separated format as single opposition copyable summary,
but for multiple oppositions (one row per opposition).
"""

from typing import Dict, List


def create_bulk_copyable_format(result: Dict) -> str:
    """
    Create tab-separated text for bulk oppositions in the same format
    as single opposition copyable summary.

    Format per row:
    Marks | US GS | INT GS | Opp Start Date | Opp End Date | Result | TM Type | Serial | TM Type | Serial | ...

    Args:
        result: Bulk scrape result from bulk_scrape_party_consolidated()

    Returns:
        String with one row per opposition, tab-separated, newline between rows
    """
    rows = []

    for opp in result.get('oppositions', []):
        # Skip failed oppositions
        if opp.get('status') == 'FAILED':
            continue

        # Skip oppositions with no marks (empty/null data)
        serial_count = opp.get('serial_count', 0)
        if serial_count == 0:
            continue

        row_data = []

        # Field 1: Marks (serial count)
        marks = str(serial_count)
        row_data.append(marks)

        # Field 2: US GS (total US classes count - with duplicates)
        us_gs = str(opp.get('total_us_class_count', 0))
        row_data.append(us_gs)

        # Field 3: INT GS (total international classes count - with duplicates)
        int_gs = str(opp.get('total_international_class_count', 0))
        row_data.append(int_gs)

        # Field 4: Opp Start Date (filing date)
        opp_start_date = opp.get('filing_date', '') or ''
        row_data.append(str(opp_start_date))

        # Field 5: Opp End Date (termination date)
        opp_end_date = opp.get('termination_date', '') or ''
        row_data.append(str(opp_end_date))

        # Field 6: Result (1=Sustained, 0=Dismissed, NA=Pending)
        opp_result = opp.get('result', None)
        if opp_result == 1:
            result_text = "1"
        elif opp_result == 0:
            result_text = "0"
        else:
            result_text = "NA"
        row_data.append(result_text)

        # Fields 7+: Alternating TM Type and Serial Number
        # Parse from comma-separated strings
        serial_numbers = opp.get('serial_numbers', '').split(', ') if opp.get('serial_numbers') else []
        mark_types = opp.get('mark_types', '').split(', ') if opp.get('mark_types') else []

        for i in range(len(serial_numbers)):
            tm_type = mark_types[i] if i < len(mark_types) else '0'
            serial_no = serial_numbers[i]
            row_data.append(str(tm_type))
            row_data.append(str(serial_no))

        # Join with tabs and add to rows
        rows.append('\t'.join(row_data))

    # Join rows with newlines
    return '\n'.join(rows)


def create_bulk_copyable_excel(result: Dict) -> bytes:
    """
    Create Excel file with bulk opposition data in copyable format.
    One row per opposition, matching single opposition copyable format.

    Args:
        result: Bulk scrape result from bulk_scrape_party_consolidated()

    Returns:
        bytes: Excel file content
    """
    import pandas as pd
    import io
    from openpyxl.styles import Font, Alignment, PatternFill

    output = io.BytesIO()

    all_rows = []
    max_serials = 0

    # First pass: determine max number of serials for column headers
    for opp in result.get('oppositions', []):
        if opp.get('status') == 'FAILED':
            continue
        serial_count = opp.get('serial_count', 0)
        if serial_count > max_serials:
            max_serials = serial_count

    # Build column headers
    columns = ['Marks', 'US GS', 'INT GS', 'Opp Start Date', 'Opp End Date', 'Result']
    for i in range(1, max_serials + 1):
        columns.append(f'TM Type {i}')
        columns.append(f'Serial No {i}')

    # Build rows
    for opp in result.get('oppositions', []):
        if opp.get('status') == 'FAILED':
            continue

        # Skip oppositions with no marks (empty/null data)
        serial_count = opp.get('serial_count', 0)
        if serial_count == 0:
            continue

        row = {
            'Marks': serial_count,
            'US GS': opp.get('total_us_class_count', 0),
            'INT GS': opp.get('total_international_class_count', 0),
            'Opp Start Date': opp.get('filing_date', ''),
            'Opp End Date': opp.get('termination_date', ''),
            'Result': '1' if opp.get('result') == 1 else '0' if opp.get('result') == 0 else 'NA'
        }

        # Add TM Types and Serial Numbers
        serial_numbers = opp.get('serial_numbers', '').split(', ') if opp.get('serial_numbers') else []
        mark_types = opp.get('mark_types', '').split(', ') if opp.get('mark_types') else []

        for i in range(max_serials):
            if i < len(serial_numbers):
                row[f'TM Type {i+1}'] = mark_types[i] if i < len(mark_types) else '0'
                row[f'Serial No {i+1}'] = serial_numbers[i]
            else:
                row[f'TM Type {i+1}'] = ''
                row[f'Serial No {i+1}'] = ''

        all_rows.append(row)

    # Create DataFrame
    df = pd.DataFrame(all_rows, columns=columns)

    # Write to Excel
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name='Oppositions', index=False)

        # Format
        workbook = writer.book
        sheet = workbook['Oppositions']

        # Header styling
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
            adjusted_width = min(max_length + 2, 20)
            sheet.column_dimensions[column_letter].width = adjusted_width

    return output.getvalue()
