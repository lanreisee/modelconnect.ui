import pytest
import pandas as pd
import os
import sys
from pathlib import Path

# Add the src directory to the Python path to import the parser module
src_path = Path(__file__).parent.parent / 'src'
sys.path.insert(0, str(src_path))

from parser import parse_spreadsheet # noqa: E402 - Import after path modification

# --- Test Fixtures ---

@pytest.fixture(scope="function") # Recreate files for each test function
def sample_csv_file(tmp_path):
    """Creates a sample CSV file for testing."""
    file_path = tmp_path / "test_data.csv"
    data = [{
        "name": "Test Model CSV",
        "description": "Description from CSV.",
        "modelStage": "Development",
        "custom.Overview.Name of the AI Solution": "CSV AI Solution",
        "empty_column": None,
        "another_empty": "",
        "numeric_val": 123,
        "bool_val": True # Note: CSVs don't inherently have bools, often read as string
    }]
    df = pd.DataFrame(data)
    df.to_csv(file_path, index=False)
    return file_path

@pytest.fixture(scope="function")
def sample_excel_file(tmp_path):
    """Creates a sample Excel (.xlsx) file for testing."""
    file_path = tmp_path / "test_data.xlsx"
    data = [{
        "name": "Test Model Excel",
        "description": "Description from Excel.",
        "modelStage": "Production",
        "custom.Accountability.Who is the business sponsor?": "Excel Sponsor",
        "empty_column": None,
        "another_empty": "",
        "numeric_val": 456.7,
        "bool_val": False
    }]
    df = pd.DataFrame(data)
    # Requires openpyxl
    df.to_excel(file_path, index=False, engine='openpyxl')
    return file_path

@pytest.fixture(scope="function")
def empty_csv_file(tmp_path):
    """Creates an empty CSV file."""
    file_path = tmp_path / "empty.csv"
    file_path.touch() # Create an empty file
    return file_path

@pytest.fixture(scope="function")
def header_only_csv_file(tmp_path):
    """Creates a CSV file with only headers."""
    file_path = tmp_path / "header_only.csv"
    df = pd.DataFrame(columns=["col1", "col2"])
    df.to_csv(file_path, index=False)
    return file_path

# --- Test Cases ---

def test_parse_valid_csv(sample_csv_file):
    """Tests parsing a valid CSV file."""
    expected_data = {
        "name": "Test Model CSV",
        "description": "Description from CSV.",
        "modelStage": "Development",
        "custom.Overview.Name of the AI Solution": "CSV AI Solution",
        "numeric_val": 123, # Pandas usually infers numeric types
        "bool_val": True # Pandas correctly infers boolean from 'True'/'False' in CSV
    }
    result = parse_spreadsheet(str(sample_csv_file))
    assert result is not None
    # Convert numeric types back to string for comparison if needed, or compare types
    assert result.get("numeric_val") == expected_data["numeric_val"]
    assert result.get("bool_val") is expected_data["bool_val"] # Check boolean value directly
    assert result.get("name") == expected_data["name"]
    assert "empty_column" not in result # Should be filtered out
    assert "another_empty" not in result # Should be filtered out

def test_parse_valid_excel(sample_excel_file):
    """Tests parsing a valid Excel file."""
    expected_data = {
        "name": "Test Model Excel",
        "description": "Description from Excel.",
        "modelStage": "Production",
        "custom.Accountability.Who is the business sponsor?": "Excel Sponsor",
        "numeric_val": 456.7,
        "bool_val": False # Excel preserves boolean type
    }
    result = parse_spreadsheet(str(sample_excel_file))
    assert result is not None
    assert result == expected_data # Direct comparison should work better for Excel

def test_parse_file_not_found():
    """Tests parsing a non-existent file."""
    result = parse_spreadsheet("non_existent_file.csv")
    assert result is None

def test_parse_unsupported_format(tmp_path):
    """Tests parsing an unsupported file format."""
    file_path = tmp_path / "test.txt"
    file_path.write_text("This is not a spreadsheet.")
    result = parse_spreadsheet(str(file_path))
    assert result is None

def test_parse_empty_csv(empty_csv_file):
    """Tests parsing an empty CSV file."""
    result = parse_spreadsheet(str(empty_csv_file))
    assert result is None # Expect None due to EmptyDataError or similar pandas handling

def test_parse_header_only_csv(header_only_csv_file):
    """Tests parsing a CSV with only headers."""
    result = parse_spreadsheet(str(header_only_csv_file))
    assert result is None # Expect None as there are no data rows

# Add more tests as needed, e.g., for different data types, edge cases, malformed files.
