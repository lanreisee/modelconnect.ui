import pandas as pd
import logging
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def parse_spreadsheet(file_path: str) -> Optional[Dict[str, Any]]:
    """
    Parses a CSV or Excel file to extract model card data from the first row.

    Args:
        file_path: The path to the spreadsheet file (.csv or .xlsx).

    Returns:
        A dictionary containing the data from the first row, with column headers
        as keys, or None if parsing fails. Returns only non-empty values.
    """
    data_dict = None
    try:
        if file_path.lower().endswith('.csv'):
            df = pd.read_csv(file_path, nrows=1) # Read only the first data row
        elif file_path.lower().endswith(('.xlsx', '.xls')):
            # Use openpyxl for .xlsx, xlrd might be needed for .xls (install if necessary)
            engine = 'openpyxl' if file_path.lower().endswith('.xlsx') else None
            df = pd.read_excel(file_path, nrows=1, engine=engine) # Read only the first data row
        else:
            logging.error(f"Unsupported file format: {file_path}. Please use CSV or Excel.")
            return None

        if df.empty:
            logging.warning(f"Spreadsheet is empty: {file_path}")
            return None

        # Convert the first row to a dictionary, handling potential NaN values
        # Fill NaN with None, then filter out None values and empty strings
        data_dict = df.iloc[0].fillna('').to_dict()
        data_dict = {k: v for k, v in data_dict.items() if pd.notna(v) and v != ''}

        logging.info(f"Successfully parsed data from: {file_path}")
        return data_dict

    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
        return None
    except pd.errors.EmptyDataError:
        logging.warning(f"Spreadsheet is empty or contains no data: {file_path}")
        return None
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
            "empty_column": None # Example of an empty value
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
    parsed_data_csv = parse_spreadsheet(test_csv_path)
    if parsed_data_csv:
        print("Parsed CSV Data:")
        for key, value in parsed_data_csv.items():
            print(f"  '{key}': '{value}'")

    print("\n--- Testing Excel ---")
    parsed_data_excel = parse_spreadsheet(test_excel_path)
    if parsed_data_excel:
        print("Parsed Excel Data:")
        for key, value in parsed_data_excel.items():
            print(f"  '{key}': '{value}'")

    print("\n--- Testing Non-existent file ---")
    parse_spreadsheet("non_existent_file.csv")

    print("\n--- Testing Unsupported format ---")
    parse_spreadsheet("sample.txt")
