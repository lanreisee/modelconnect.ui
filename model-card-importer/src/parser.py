import pandas as pd
import logging
from typing import Dict, Any, Optional, List

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def parse_spreadsheet(file_path: str) -> Optional[List[Dict[str, Any]]]:
    """
    Parses a CSV or Excel file to extract model card data from all rows.

    Args:
        file_path: The path to the spreadsheet file (.csv or .xlsx).

    Returns:
        A list of dictionaries, where each dictionary represents a row
        with column headers as keys, or None if parsing fails.
        Only non-empty values are included in each dictionary.
    """
    records = None
    try:
        if file_path.lower().endswith('.csv'):
            # Read all rows, keep empty values as empty strings during read
            df = pd.read_csv(file_path, keep_default_na=False, na_values=[''])
        elif file_path.lower().endswith(('.xlsx', '.xls')):
            # Use openpyxl for .xlsx, xlrd might be needed for .xls (install if necessary)
            engine = 'openpyxl' if file_path.lower().endswith('.xlsx') else None
            # Read all rows, keep empty values as empty strings during read
            df = pd.read_excel(file_path, keep_default_na=False, na_values=[''], engine=engine)
        else:
            logging.error(f"Unsupported file format: {file_path}. Please use CSV or Excel.")
            return None

        if df.empty:
            logging.warning(f"Spreadsheet is empty or contains only headers: {file_path}")
            return [] # Return empty list if only headers or completely empty

        # Convert DataFrame to list of dictionaries
        # Fill any remaining NaN specifically with None for consistent handling
        df = df.fillna('') # Replace NaN with empty string before filtering
        records = df.to_dict(orient='records')

        # Filter out empty values from each record dictionary
        filtered_records = []
        for record in records:
            filtered_record = {k: v for k, v in record.items() if pd.notna(v) and v != ''}
            if filtered_record: # Only add if the record is not entirely empty after filtering
                filtered_records.append(filtered_record)

        logging.info(f"Successfully parsed {len(filtered_records)} records from: {file_path}")
        return filtered_records

    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
        return None
    except pd.errors.EmptyDataError: # This might not trigger if headers exist
        logging.warning(f"Spreadsheet file is completely empty (no headers): {file_path}")
        return []
    except Exception as e:
        logging.error(f"Error parsing spreadsheet {file_path}: {e}", exc_info=True)
        return None

if __name__ == '__main__':
    # Example usage (for testing purposes)
    # Create dummy files first or replace with actual paths
    test_csv_path = '../data/sample_card.csv'
    test_excel_path = '../data/sample_card.xlsx'

    # --- Create dummy CSV for testing ---
    try:
        import os
        os.makedirs('../data', exist_ok=True)
        dummy_df_csv = pd.DataFrame([{
            "name": "Test Model CSV",
            "description": "Description from CSV.",
            "modelStage": "Development",
            "custom.Overview.Name of the AI Solution": "CSV AI Solution",
            "empty_column": None, # Example of an empty value
            "another_empty": ""
        }, { # Add a second row
            "name": "Test Model CSV 2",
            "description": "Second row description.",
            "modelStage": "Testing",
            "custom.Overview.Name of the AI Solution": "CSV AI Solution 2",
            "empty_column": "Has Value",
            "another_empty": "",
            "numeric_val": 456,
            "bool_val": False
        }])
        dummy_df_csv.to_csv(test_csv_path, index=False)
        logging.info(f"Created dummy CSV: {test_csv_path}")
    except Exception as e:
        logging.warning(f"Could not create dummy CSV: {e}")
    # ------------------------------------

     # --- Create dummy Excel for testing ---
    try:
        import os
        os.makedirs('../data', exist_ok=True)
        dummy_df_xlsx = pd.DataFrame([{
            "name": "Test Model Excel",
            "description": "Description from Excel.",
            "modelStage": "Production",
            "custom.Accountability.Who is the business sponsor?": "Excel Sponsor",
            "another_empty_col": "" # Example of empty string
        }])
        # Requires openpyxl: pip install openpyxl
        dummy_df_xlsx.to_excel(test_excel_path, index=False, engine='openpyxl')
        logging.info(f"Created dummy Excel: {test_excel_path}")
    except Exception as e:
        logging.warning(f"Could not create dummy Excel (ensure openpyxl is installed): {e}")
    # ------------------------------------


    print("\n--- Testing CSV ---")
    parsed_records_csv = parse_spreadsheet(test_csv_path)
    if parsed_records_csv is not None:
        print(f"Parsed CSV Data ({len(parsed_records_csv)} records):")
        for i, record in enumerate(parsed_records_csv):
            print(f"  Record {i+1}:")
            for key, value in record.items():
                print(f"    '{key}': '{value}'")

    print("\n--- Testing Excel ---")
    parsed_records_excel = parse_spreadsheet(test_excel_path)
    if parsed_records_excel is not None:
        print(f"Parsed Excel Data ({len(parsed_records_excel)} records):")
        for i, record in enumerate(parsed_records_excel):
             print(f"  Record {i+1}:")
             for key, value in record.items():
                print(f"    '{key}': '{value}'")

    print("\n--- Testing Non-existent file ---")
    parse_spreadsheet("non_existent_file.csv")

    print("\n--- Testing Unsupported format ---")
    parse_spreadsheet("sample.txt")
