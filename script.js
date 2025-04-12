document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('modelCardForm');
    const messageArea = document.getElementById('messageArea');
    // Placeholder API endpoint - replace with your actual backend endpoint
    const API_ENDPOINT = '/api/modelcard';

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
    const modelForm = document.getElementById('modelCardForm'); // Get the form element

    if (importButton && fileInput && modelForm && importMessageArea) {
        importButton.addEventListener('click', async () => {
            importMessageArea.textContent = '';
            importMessageArea.className = 'message-area'; // Reset class

            if (fileInput.files.length === 0) {
                importMessageArea.textContent = 'Please select a file first.';
                importMessageArea.className = 'message-area error';
                return;
            }

            const file = fileInput.files[0];
            const formData = new FormData();
            formData.append('file', file);

            // Assume Flask server is running on port 5001
            const uploadUrl = 'http://127.0.0.1:5001/upload-for-form';

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

                // Clear existing form fields before populating
                modelForm.reset();
                // Also clear the main submit message area if needed
                const mainMessageArea = document.getElementById('messageArea');
                if (mainMessageArea) {
                    mainMessageArea.textContent = '';
                    mainMessageArea.className = '';
                }


                // Populate the form
                let fieldsPopulated = 0;
                for (const key in result) {
                    const field = modelForm.elements[key]; // Access form elements by name/id
                    if (field) {
                        field.value = result[key];
                        fieldsPopulated++;
                        // Optional: If you want to open the accordion section containing the populated field
                        const section = field.closest('.accordion-item');
                        if (section) {
                            const header = section.querySelector('.accordion-header');
                            const content = section.querySelector('.accordion-content');
                            if (header && content && !header.classList.contains('active')) {
                                // This logic might open multiple sections if data spans across them.
                                // Consider if you only want the *first* populated section opened,
                                // or maybe just leave them closed for the user to review.
                                // For simplicity now, let's not auto-open them on import.
                                // header.classList.add('active');
                                // content.style.display = 'block';
                                // content.classList.add('active');
                            }
                        }
                    } else {
                        console.warn(`Form field with name/id '${key}' not found.`);
                    }
                }

                importMessageArea.textContent = `Successfully loaded data for ${fieldsPopulated} field(s) from ${file.name}. Please review and submit.`;
                importMessageArea.className = 'message-area success';
                fileInput.value = ''; // Clear the file input

            } catch (error) {
                console.error('Error importing file:', error);
                importMessageArea.textContent = `Error: ${error.message}`;
                importMessageArea.className = 'message-area error';
            }
        });
    } else {
         console.error('Import elements not found (spreadsheetFile, importSpreadsheetButton, modelCardForm, or importMessageArea)');
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

            console.log('Submitting data:', data); // Log data before sending

            try {
                // Send data to the placeholder API endpoint
                const response = await fetch(API_ENDPOINT, {
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
                // A real backend might return 201 Created on success.

                // Simulate success - a real API would provide a meaningful response
                console.log('Placeholder response received:', response);
                messageArea.textContent = 'Model card data submitted successfully (Placeholder)!';
                messageArea.className = 'success';
                form.reset(); // Optionally clear the form on success

                // Handle potential non-OK responses if the placeholder *did* respond
                if (!response.ok) {
                     // Attempt to read error message if backend sent one
                    let errorMsg = `HTTP error! Status: ${response.status}`;
                    try {
                        const errorData = await response.json();
                        errorMsg = errorData.message || JSON.stringify(errorData);
                    } catch (e) {
                        // Ignore if response body isn't JSON
                    }
                    throw new Error(errorMsg);
                }


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
