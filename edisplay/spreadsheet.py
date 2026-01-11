import json
import logging
from datetime import datetime

from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

from edisplay.secrets import get_config


SCOPES = [
    'https://www.googleapis.com/auth/spreadsheets',
    'https://www.googleapis.com/auth/drive.metadata.readonly'
]


def get_table_id(spreadsheet_id, sheet_name, table_name):
    try:
        creds = Credentials.from_service_account_file('google_credentials.json', scopes=SCOPES)
        
        # Get spreadsheet data including tables
        sheets_service = build('sheets', 'v4', credentials=creds)
        spreadsheet = sheets_service.spreadsheets().get(
            spreadsheetId=spreadsheet_id,
            includeGridData=False
        ).execute()
        
        # Find the sheet and look for tables
        for sheet in spreadsheet.get('sheets', []):
            if sheet['properties']['title'] == sheet_name:
                if 'tables' in sheet:
                    logging.debug(f"\nTables found in sheet '{sheet_name}':")
                    for table in sheet['tables']:
                        table_id = table.get('tableId')
                        table_display_name = table.get('name', 'Unnamed')
                        
                        # Get column names
                        columns = table.get('columnProperties', [])
                        col_names = [col.get('columnName', 'N/A') for col in columns[:4]]
                        
                        logging.debug(f"  - Table Name: '{table_display_name}'")
                        logging.debug(f"    Table ID: {table_id}")
                        logging.debug(f"    Columns: {col_names}")
                        
                        # If table_name specified, try to match it
                        if table_name:
                            if table_display_name == table_name:
                                logging.debug(f"\n✓ Found table '{table_name}' with ID: {table_id}")
                                return table_id
                        else:
                            # Return first table if no name specified
                            logging.debug(f"\nUsing table '{table_display_name}' (ID: {table_id})")
                            return table_id
                    
                    # If we get here and table_name was specified, we couldn't find it
                    if table_name:
                        logging.debug(f"\n⚠ Could not find table named '{table_name}'")
                        logging.debug("Available tables listed above. Returning first table.")
                        return sheet['tables'][0].get('tableId')
                    
                else:
                    logging.debug(f"No tables found in sheet: {sheet_name}")
                    logging.debug("Note: Make sure you have an actual Table created in Google Sheets")
                    logging.debug("(Insert > Table, not just formatted cells)")
                    return None
        
        logging.debug(f"Sheet '{sheet_name}' not found")
        return None
        
    except Exception as e:
        logging.debug(f"Error getting table ID: {e}")
        import traceback
        traceback.logging.debug_exc()
        return None
    

def get_table_content(spreadsheet_id, table_id):
    try:
        creds = Credentials.from_service_account_file('google_credentials.json', scopes=SCOPES)

        # Get last modified time from Drive API
        drive_service = build('drive', 'v3', credentials=creds)
        file_metadata = drive_service.files().get(
            fileId=spreadsheet_id,
            fields='modifiedTime'
        ).execute()
        
        last_modified = file_metadata.get('modifiedTime')
        logging.debug(f"Last modified: {last_modified}")
        
        # Get spreadsheet with grid data to read table contents
        sheets_service = build('sheets', 'v4', credentials=creds)
        spreadsheet = sheets_service.spreadsheets().get(
            spreadsheetId=spreadsheet_id,
            includeGridData=True
        ).execute()
        
        # Find the table
        table_info = None
        sheet_data = None
        
        for sheet in spreadsheet.get('sheets', []):
            if 'tables' in sheet:
                for table in sheet['tables']:
                    if str(table.get('tableId')) == str(table_id):
                        table_info = table
                        sheet_data = sheet
                        break
            if table_info:
                break
        
        if not table_info:
            logging.debug(f"Table with ID {table_id} not found")
            return None
        
        # Get the table range
        table_range = table_info.get('range', {})
        start_row = table_range.get('startRowIndex', 0)
        end_row = table_range.get('endRowIndex', 0)
        start_col = table_range.get('startColumnIndex', 0)
        end_col = table_range.get('endColumnIndex', 0)
        
        # Get column names
        columns = table_info.get('columnProperties', [])
        col_names = [col.get('columnName', f'Col{i}') for i, col in enumerate(columns)]
        
        logging.debug(f"\nTable Info:")
        logging.debug(f"  Name: {table_info.get('name', 'Unnamed')}")
        logging.debug(f"  Table ID: {table_id}")
        logging.debug(f"  Rows: {start_row} to {end_row}")
        logging.debug(f"  Columns: {start_col} to {end_col}")
        logging.debug(f"  Total rows: {end_row - start_row}")
        logging.debug(f"  Column names: {col_names}")
        
        # Extract data from grid data
        grid_data = sheet_data.get('data', [{}])[0]
        row_data = grid_data.get('rowData', [])
        
        logging.debug(f"\n{'='*100}")
        logging.debug("TABLE CONTENT:")
        logging.debug(f"{'='*100}\n")
        
        # Extract and display rows
        table_rows = []
        for i in range(start_row, min(end_row, len(row_data))):
            row = row_data[i]
            values = row.get('values', [])
            
            row_values = []
            for j in range(start_col, min(end_col, len(values))):
                cell = values[j]
                # Get the formatted value or effective value
                cell_value = cell.get('formattedValue', '')
                if not cell_value:
                    effective_value = cell.get('effectiveValue', {})
                    cell_value = effective_value.get('stringValue', 
                                 effective_value.get('numberValue', 
                                 effective_value.get('boolValue', '')))
                row_values.append(str(cell_value))
            
            table_rows.append(row_values)
            
            # logging.debug row
            if i == start_row:
                # Header row
                logging.debug(" | ".join(f"{val:24}" for val in row_values))
                logging.debug("-" * 100)
            else:
                logging.debug(" | ".join(f"{val:24}" for val in row_values))
        
        logging.debug(f"\n{'='*100}")
        logging.debug(f"Total rows in table: {len(table_rows)}")
        
        return {
            'table_id': table_id,
            'table_name': table_info.get('name'),
            'columns': col_names,
            'rows': table_rows,
            'range': table_range,
            'last_modified': datetime.fromisoformat(last_modified.replace('Z', '+00:00'))
        }
        
    except Exception as e:
        logging.debug(f"Error retrieving table content: {e}")
        import traceback
        traceback.logging.debug_exc()
        return None


if __name__ == '__main__':
    spreadsheet_id = get_config('Google', 'SpreadsheetId')

    table = 'Cartes'
    worksheet_name = 'Cartes'
    # table_id = get_table_id(spreadsheet_id, worksheet_name, table)
    # logging.debug(f'Table ID for Table {table}: {table_id}')

    table_id = get_config('Google', 'TableId')    
    info = get_table_content(spreadsheet_id, table_id)
    print([{name: date} for name, _, date in info['rows'][1:]])
