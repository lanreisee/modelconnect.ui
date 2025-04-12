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
