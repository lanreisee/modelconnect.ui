import logging
from typing import Dict, Any

# Use relative imports for modules within the same package (src)
from .db_connection import get_db_connection
from .data_access import insert_model_card, FIELD_TO_COLUMN_MAP

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def save_new_model_card(model_card_data: Dict[str, Any]) -> bool:
    """
    Service layer function to handle saving a new model card.
    Orchestrates mapping, database connection, insertion, and transaction management.

    Args:
        model_card_data: Dictionary containing data from the API request
                         (keys match frontend form IDs/names).

    Returns:
        True if saving was successful, False otherwise.
    """
    cnxn = None
    success = False
    try:
        cnxn = get_db_connection()
        if not cnxn:
            # Connection error already logged by get_db_connection
            return False # Indicate failure

        # Prepare data for insertion: map keys and filter based on map
        db_data = {}
        for form_key, db_column in FIELD_TO_COLUMN_MAP.items():
            if form_key in model_card_data:
                 # Ensure None is inserted for empty strings from form if column allows NULL
                value = model_card_data[form_key]
                db_data[db_column] = value if value != '' else None
            # else:
                 # Optionally handle missing keys if needed (e.g., set default NULL)
                 # db_data[db_column] = None
                 pass # Currently, we only insert columns present in the input

        if not db_data:
             logging.warning("No valid data provided to save_new_model_card after mapping.")
             # Depending on requirements, this might be an error or just nothing to insert
             return False # Or raise a specific exception

        # Call the data access layer function to perform the insert
        insert_model_card(cnxn, db_data)

        # If insert_model_card didn't raise an exception, commit the transaction
        cnxn.commit()
        logging.info("Model card data committed successfully.")
        success = True

    except Exception as e:
        # Log the exception details
        logging.error(f"Error in service layer during model card save: {e}", exc_info=True)
        if cnxn:
            try:
                # Rollback transaction on any error during the process
                cnxn.rollback()
                logging.info("Transaction rolled back due to error.")
            except Exception as rb_ex:
                logging.error(f"Error during transaction rollback: {rb_ex}", exc_info=True)
        success = False # Ensure failure is indicated
    finally:
        if cnxn:
            cnxn.close()
            logging.info("Database connection closed in service layer.")

    return success

# Example usage (for potential future testing)
if __name__ == '__main__':
    print("This module provides service layer functions.")
    # Example:
    # test_data = {
    #     "name": "Service Test",
    #     "description": "Testing service layer save",
    #     "custom.mocApplicationFormId": "SVC-123"
    # }
    # if save_new_model_card(test_data):
    #     print("Service layer test save successful.")
    # else:
    #     print("Service layer test save failed.")
