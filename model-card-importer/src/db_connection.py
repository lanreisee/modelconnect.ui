import pyodbc
import logging
import os

# --- Configuration ---
# Ideally, load these from environment variables or a config file
# For Windows Authentication, UID/PWD are not needed in the connection string itself
SERVER_NAME = "ROSWIMLOPSDB1"
DATABASE_NAME = "ModelOp_Dev"
# Ensure you have the necessary ODBC Driver installed (e.g., ODBC Driver 17 for SQL Server)
# You might need to adjust the driver name based on your installation.
# Common names: '{ODBC Driver 17 for SQL Server}', '{SQL Server Native Client 11.0}', '{SQL Server}'
DRIVER = '{ODBC Driver 17 for SQL Server}' # Adjust if necessary

# Connection string for Windows Authentication
CONN_STRING = (
    f"DRIVER={DRIVER};"
    f"SERVER={SERVER_NAME};"
    f"DATABASE={DATABASE_NAME};"
    f"Trusted_Connection=yes;" # Key for Windows Authentication
)
# ---------------------

def get_db_connection():
    """
    Establishes and returns a pyodbc connection to the SQL Server database
    using Windows Authentication. Returns None if connection fails.
    """
    cnxn = None
    try:
        cnxn = pyodbc.connect(CONN_STRING)
        logging.info(f"Successfully connected to database: {DATABASE_NAME} on server: {SERVER_NAME}")
        return cnxn
    except pyodbc.Error as ex:
        sqlstate = ex.args[0]
        logging.error(f"Error connecting to database: {sqlstate} - {ex}")
        # You might want to check for specific SQLSTATE errors here
        return None
    except Exception as e:
        logging.error(f"An unexpected error occurred during DB connection: {e}", exc_info=True)
        return None

# Example usage (for testing connection directly)
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    print("Attempting to connect to the database...")
    connection = get_db_connection()
    if connection:
        print("Connection successful!")
        try:
            # Optional: Test executing a simple query
            cursor = connection.cursor()
            cursor.execute("SELECT @@VERSION;")
            row = cursor.fetchone()
            if row:
                print(f"SQL Server Version: {row[0]}")
            cursor.close()
        except Exception as e:
            print(f"Error executing test query: {e}")
        finally:
            connection.close()
            print("Connection closed.")
    else:
        print("Connection failed. Check configuration, driver installation, and network access.")
