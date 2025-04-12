import os
import logging
from flask import Flask, request, jsonify
from flask_cors import CORS # Import CORS
from werkzeug.utils import secure_filename
from parser import parse_spreadsheet # Import the parser function

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'uploads') # Store uploads temporarily
ALLOWED_EXTENSIONS = {'csv', 'xlsx', 'xls'}

# Ensure upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
CORS(app) # Enable CORS for the entire app
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024 # Limit upload size (e.g., 16MB)

def allowed_file(filename):
    """Checks if the file extension is allowed."""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload-for-form', methods=['POST'])
def upload_file_for_form():
    """
    Handles file upload, parses it, and returns data for form population.
    """
    if 'file' not in request.files:
        logging.warning("No file part in request")
        return jsonify({"error": "No file part in the request"}), 400

    file = request.files['file']

    if file.filename == '':
        logging.warning("No selected file")
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename) # Sanitize filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)

        try:
            file.save(file_path)
            logging.info(f"File saved temporarily to: {file_path}")

            # Parse the saved spreadsheet
            parsed_data = parse_spreadsheet(file_path)

            # Clean up the uploaded file after parsing
            try:
                os.remove(file_path)
                logging.info(f"Removed temporary file: {file_path}")
            except OSError as e:
                logging.error(f"Error removing temporary file {file_path}: {e}")

            if parsed_data is None:
                logging.error(f"Parsing failed for file: {filename}")
                return jsonify({"error": "Failed to parse spreadsheet data. Check file format and content."}), 500
            else:
                logging.info(f"Successfully parsed data for {filename}")
                return jsonify(parsed_data), 200

        except Exception as e:
            logging.error(f"Error during file processing {filename}: {e}", exc_info=True)
            # Attempt to clean up file even if error occurs during processing
            if os.path.exists(file_path):
                 try:
                    os.remove(file_path)
                    logging.info(f"Removed temporary file after error: {file_path}")
                 except OSError as e_rem:
                    logging.error(f"Error removing temporary file {file_path} after error: {e_rem}")
            return jsonify({"error": f"An internal error occurred: {e}"}), 500
    else:
        logging.warning(f"File type not allowed: {file.filename}")
        return jsonify({"error": "File type not allowed. Please upload CSV or Excel files."}), 400

# Basic route for testing if the server is running
@app.route('/')
def index():
    return "Model Card Importer API is running!"

if __name__ == '__main__':
    # Note: For development only. Use a proper WSGI server (like Gunicorn or Waitress) for production.
    logging.info("Starting Flask development server...")
    app.run(debug=True, port=5001) # Run on a different port than default 5000 if needed
