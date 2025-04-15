import os
import logging
import shutil
# Removed pyodbc import
from fastapi import FastAPI, File, UploadFile, HTTPException, status, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, Optional, List

# Use relative import since parser.py and services.py are in the same directory
from .parser import parse_spreadsheet
from .services import save_new_model_card # Import the service function
# Removed db_connection import

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'temp_uploads')
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = FastAPI(title="Model Card Importer API")

# Configure CORS
origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Field Mapping Removed - Now handled in data_access.py ---
# ---------------------------------------------------------


def allowed_file(filename):
    """Checks if the file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.post("/upload-for-form", response_model=Optional[List[Dict[str, Any]]])
async def upload_file_for_form(file: UploadFile = File(...)):
    """
    Handles spreadsheet upload, parses all rows, and returns data
    for form population.
    """
    if not allowed_file(file.filename):
        logging.warning(f"File type not allowed: {file.filename}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File type not allowed. Please upload CSV or Excel files."
        )

    temp_file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    try:
        # Save the uploaded file temporarily
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logging.info(f"File saved temporarily to: {temp_file_path}")

        # Parse the saved spreadsheet
        parsed_data = parse_spreadsheet(temp_file_path)

        if parsed_data is None:
            # This case might occur if parser.py had an internal error returning None
            # instead of an empty list for empty files.
            logging.error(f"Parsing returned None for file: {file.filename}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to parse spreadsheet data. Parser returned None."
            )
        elif not isinstance(parsed_data, list):
             # Defensive check: Ensure parser actually returned a list
             logging.error(f"Parser returned non-list type: {type(parsed_data)} for file: {file.filename}")
             raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal error: Parser did not return expected data format."
             )

        logging.info(f"Successfully parsed data for {file.filename}")
        # --- Detailed logging removed ---
        return parsed_data

    except HTTPException as http_exc:
        # Re-raise HTTPExceptions directly
        raise http_exc
    except Exception as e:
        logging.error(f"Error during file processing {file.filename}: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An internal server error occurred: {e}"
        )
    finally:
        # Ensure the temporary file is deleted
        if os.path.exists(temp_file_path):
            try:
                os.remove(temp_file_path)
                logging.info(f"Removed temporary file: {temp_file_path}")
            except OSError as e_rem:
                logging.error(f"Error removing temporary file {temp_file_path}: {e_rem}")
        # Close the file stream associated with UploadFile
        await file.close()


@app.post("/save-model-card")
async def save_model_card(model_card_data: Dict[str, Any] = Body(...)):
    """
    Receives model card data (presumably from the frontend form submission)
    and passes it to the service layer for saving.
    """
    try:
        # Call the service layer function to handle the save logic
        success = save_new_model_card(model_card_data)

        if success:
            logging.info("API endpoint returning successful save message.")
            return {"message": "Model card data saved successfully."}
        else:
            # If service layer returned False, it means an error occurred and was logged
            # Raise a generic internal server error for the client
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                                detail="Failed to save model card data due to an internal error.")

    except ValueError as ve: # Catch potential validation errors from service/data layer
         logging.error(f"Validation error saving model card data: {ve}", exc_info=True)
         raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
    except Exception as e:
        # Catch any other unexpected errors from the service layer
        logging.error(f"Unexpected error in save endpoint: {e}", exc_info=True)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=f"An unexpected internal error occurred: {e}")


@app.get("/")
async def root():
    """Basic route for testing if the server is running."""
    return {"message": "Model Card Importer API is running!"}

# Note: Running with uvicorn is preferred for FastAPI
# Example command: uvicorn src.app:app --reload --port 5001 --host 0.0.0.0
# The __main__ block is less common for FastAPI but can be used for simple cases
if __name__ == "__main__":
    import uvicorn
    logging.info("Starting FastAPI server with Uvicorn...")
    # Run directly for simple testing; use command line for more control
    uvicorn.run("app:app", host="127.0.0.1", port=5001, log_level="info", reload=True) # Use string format for reload
