import os
import logging
import shutil
from fastapi import FastAPI, File, UploadFile, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, Optional

# Use relative import since parser.py is in the same directory
from .parser import parse_spreadsheet

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuration
# Use a temporary directory within the project for uploads
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'temp_uploads')
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = FastAPI(title="Model Card Importer API")

# Configure CORS
# Allows requests from all origins (*) - restrict in production if needed
origins = ["*"] # Or specify origins like ["http://localhost", "http://127.0.0.1"] if frontend is served
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods (GET, POST, etc.)
    allow_headers=["*"], # Allows all headers
)

def allowed_file(filename):
    """Checks if the file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.post("/upload-for-form", response_model=Optional[Dict[str, Any]])
async def upload_file_for_form(file: UploadFile = File(...)):
    """
    Handles spreadsheet upload, parses the first row, and returns data
    for form population.
    """
    if not allowed_file(file.filename):
        logging.warning(f"File type not allowed: {file.filename}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File type not allowed. Please upload CSV or Excel files."
        )

    # Sanitize filename (though less critical for temp files)
    # filename = secure_filename(file.filename) # werkzeug.utils not needed directly
    temp_file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    try:
        # Save the uploaded file temporarily
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        logging.info(f"File saved temporarily to: {temp_file_path}")

        # Parse the saved spreadsheet
        parsed_data = parse_spreadsheet(temp_file_path)

        if parsed_data is None:
            logging.error(f"Parsing failed for file: {file.filename}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to parse spreadsheet data. Check file format and content."
            )

        logging.info(f"Successfully parsed data for {file.filename}")
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
    uvicorn.run(app, host="127.0.0.1", port=5001, log_level="info")
