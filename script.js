document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('modelCardForm');
    const messageArea = document.getElementById('messageArea'); // For submit messages
    // API endpoint for saving data (points to our FastAPI server)
    const SAVE_API_ENDPOINT = 'http://127.0.0.1:5001/save-model-card';
    // API endpoint for uploading spreadsheet (points to our FastAPI server)
    const UPLOAD_API_ENDPOINT = 'http://127.0.0.1:5001/upload-for-form';


    // --- Accordion Logic ---
    const accordionHeaders = document.querySelectorAll('.accordion-header');

    accordionHeaders.forEach(header => {
        header.addEventListener('click', () => {
            const content = header.nextElementSibling;
            const currentlyActive = document.querySelector('.accordion-header.active');

            // Close other sections if one is open and we're clicking a different header
            if (currentlyActive && currentlyActive !== header) {
                currentlyActive.classList.remove('active');
                currentlyActive.nextElementSibling.style.display = 'none';
                currentlyActive.nextElementSibling.classList.remove('active');
            }

            // Toggle the clicked section
            header.classList.toggle('active');
            if (content.style.display === 'block') {
                content.style.display = 'none';
                content.classList.remove('active');
            } else {
                content.style.display = 'block';
                content.classList.add('active');
            }
        });

        // Optionally, open the first section by default
        if (header === accordionHeaders[0]) {
             header.classList.add('active');
             header.nextElementSibling.style.display = 'block';
             header.nextElementSibling.classList.add('active');
        } else {
            header.nextElementSibling.style.display = 'none'; // Ensure others start closed
        }
    });
    // --- End Accordion Logic ---

    // --- Spreadsheet Import Logic ---
    const fileInput = document.getElementById('spreadsheetFile');
    const importButton = document.getElementById('importSpreadsheetButton');
    const importMessageArea = document.getElementById('importMessageArea');
    const modelForm = document.getElementById('modelCardForm');
    const recordNavDiv = document.getElementById('recordNavigation');
    const prevButton = document.getElementById('prevRecordButton');
    const nextButton = document.getElementById('nextRecordButton');
    const recordCounterSpan = document.getElementById('recordCounter');

    let importedRecords = []; // To store the array of records from the file
    let currentRecordIndex = -1; // Index of the currently displayed record

    // Function to display a specific record in the form
    function displayRecord(index) {
        if (index < 0 || index >= importedRecords.length) {
            console.error("Invalid record index:", index);
            return;
        }
        currentRecordIndex = index;
        const record = importedRecords[index];

        // --- Close all accordion sections first ---
        accordionHeaders.forEach(header => {
            const content = header.nextElementSibling;
            header.classList.remove('active');
            if (content && content.classList.contains('accordion-content')) {
                content.classList.remove('active');
                content.style.display = 'none';
            }
        });
        // -----------------------------------------

        // Clear existing form fields before populating
        modelForm.reset();

        const sectionsToOpen = new Set(); // Keep track of sections with data

        // Populate the form and identify sections to open
        for (const key in record) {
            console.log(`Processing key: "${key}", Value: "${record[key]}"`); // DEBUG: Log key and value
            // Try finding field by ID directly, then try prepending "custom."
            let field = document.getElementById(key);
            if (!field) {
                // If direct key fails, try adding the 'custom.' prefix
                const prefixedKey = 'custom.' + key;
                console.log(`   Field not found with key "${key}", trying "${prefixedKey}"`); // DEBUG
                field = document.getElementById(prefixedKey);
            }

            if (field && field.form === modelForm) { // Check if the found element belongs to our form
                 console.log(`   Found field:`, field); // DEBUG: Log the found field element
                 // Handle different input types if necessary in the future (e.g., checkboxes)
                 // For now, assuming all are text/textarea
                field.value = record[key];
                console.log(`   Set field value to: "${field.value}"`); // DEBUG: Confirm value was set

                // Find the parent accordion item and mark it for opening
                const sectionItem = field.closest('.accordion-item');
                if (sectionItem) {
                    sectionsToOpen.add(sectionItem);
                }

            } else {
                console.warn(`Form field with name/id '${key}' not found for record ${index}.`);
            }
        }

        // --- Open sections that received data ---
        sectionsToOpen.forEach(sectionItem => {
            const header = sectionItem.querySelector('.accordion-header');
            const content = sectionItem.querySelector('.accordion-content');
            if (header && content) {
                header.classList.add('active');
                content.classList.add('active');
                content.style.display = 'block';
            }
        });
        // --------------------------------------

        // Update navigation controls
        recordCounterSpan.textContent = `Record ${index + 1} of ${importedRecords.length}`;
        prevButton.disabled = (index === 0);
        nextButton.disabled = (index === importedRecords.length - 1);
        recordNavDiv.style.display = 'block'; // Show navigation
    }

    if (importButton && fileInput && modelForm && importMessageArea && recordNavDiv && prevButton && nextButton && recordCounterSpan) {
        importButton.addEventListener('click', async () => {
            // Reset state before import
            importMessageArea.textContent = '';
            importMessageArea.className = 'message-area';
            recordNavDiv.style.display = 'none';
            importedRecords = [];
            currentRecordIndex = -1;
            modelForm.reset(); // Clear form

            if (fileInput.files.length === 0) {
                importMessageArea.textContent = 'Please select a file first.';
                importMessageArea.className = 'message-area error';
                return;
            }

            const file = fileInput.files[0];
            const formData = new FormData();
            formData.append('file', file);

            // Assume Flask server is running on port 5001
            // Use the constant for the upload URL
            const uploadUrl = UPLOAD_API_ENDPOINT;

            try {
                importMessageArea.textContent = 'Uploading and processing...';
                importMessageArea.className = 'message-area info'; // Use a neutral class for processing

                const response = await fetch(uploadUrl, {
                    method: 'POST',
                    body: formData,
                    // Note: Don't set Content-Type header when sending FormData,
                    // the browser does it automatically with the correct boundary.
                });

                const result = await response.json();

                if (!response.ok) {
                    throw new Error(result.error || `HTTP error! Status: ${response.status}`);
                }

                // --- Handle multiple records ---
                if (Array.isArray(result) && result.length > 0) {
                    importedRecords = result; // Store the array
                    displayRecord(0); // Display the first record
                    importMessageArea.textContent = `Successfully loaded ${importedRecords.length} record(s) from ${file.name}.`;
                    importMessageArea.className = 'message-area success';
                } else if (Array.isArray(result) && result.length === 0) {
                    importMessageArea.textContent = 'Spreadsheet parsed, but no data rows found.';
                    importMessageArea.className = 'message-area warning'; // Use a warning style
                     recordNavDiv.style.display = 'none'; // Hide nav if no records
                }
                 else {
                     // Handle case where API might return non-array or unexpected format
                     console.error("Received unexpected data format from API:", result);
                     throw new Error("Received unexpected data format from server.");
                 }
                // --------------------------------

                fileInput.value = ''; // Clear the file input

            } catch (error) {
                console.error('Error importing file:', error);
                importMessageArea.textContent = `Error: ${error.message}`;
                importMessageArea.className = 'message-area error';
            }
        });
    } else {
         console.error('Import elements not found (spreadsheetFile, importSpreadsheetButton, modelCardForm, importMessageArea, recordNavDiv, prevButton, nextButton, recordCounterSpan)');
    }

    // Add event listeners for Prev/Next buttons
    if(prevButton && nextButton) {
        prevButton.addEventListener('click', () => {
            if (currentRecordIndex > 0) {
                displayRecord(currentRecordIndex - 1);
            }
        });

        nextButton.addEventListener('click', () => {
            if (currentRecordIndex < importedRecords.length - 1) {
                displayRecord(currentRecordIndex + 1);
            }
        });
    }
    // --- End Spreadsheet Import Logic ---


    if (form) {
        form.addEventListener('submit', async (event) => {
            event.preventDefault(); // Prevent default browser form submission
            messageArea.textContent = ''; // Clear previous messages
            messageArea.className = ''; // Reset message area class

            const formData = new FormData(form);
            const data = {};

            // Convert FormData to a plain object
            // Handles fields with names like "custom.Overview.Name of the AI Solution"
            formData.forEach((value, key) => {
                // Basic handling for nested structure based on '.'
                // This creates a simple key-value structure, not deeply nested.
                // For a truly nested structure, more complex parsing would be needed.
                data[key] = value;
            });

            console.log('Submitting data to save:', data); // Log data before sending

            try {
                // Send data to the *actual* save endpoint
                const response = await fetch(SAVE_API_ENDPOINT, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify(data),
                });

                // Check if the placeholder response is 'ok' (status 200-299)
                // In a real scenario, the backend would return appropriate status codes.
                // Since this is a placeholder, we might not get a real response,
                // so we'll simulate success for now unless fetch itself throws an error.
                // A real backend might return 201 Created or 200 OK on success.

                const result = await response.json(); // Get response from backend

                if (!response.ok) {
                    // Use error message from backend if available
                    throw new Error(result.detail || result.error || `HTTP error! Status: ${response.status}`);
                }

                console.log('Save response received:', result);
                messageArea.textContent = result.message || 'Model card data saved successfully!'; // Use message from backend
                messageArea.className = 'message-area success'; // Use specific class
                form.reset(); // Clear the form on success
                // Optionally hide record navigation if needed after successful save
                // if (recordNavDiv) recordNavDiv.style.display = 'none';
                // importedRecords = [];
                // currentRecordIndex = -1;


            } catch (error) {
                console.error('Error submitting form:', error);
                messageArea.textContent = `Error submitting data: ${error.message}. Check console for details.`;
                messageArea.className = 'error';
            }
        });
    } else {
        console.error('Form element #modelCardForm not found.');
        messageArea.textContent = 'Error: Form could not be initialized.';
        messageArea.className = 'error';
    }
});
