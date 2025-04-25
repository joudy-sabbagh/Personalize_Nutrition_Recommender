import psycopg2
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Database connection parameters from environment variables
host = os.getenv("DB_HOST")
user = os.getenv("DB_USER")
password = os.getenv("DB_PASSWORD")
port = os.getenv("DB_PORT")

# Connect to the `postgres` database (the default administrative database)
conn = psycopg2.connect(
    host=host,
    database="postgres",  # Default database for administrative tasks
    user=user,
    password=password,
    port=port
)

# Set autocommit to True to allow CREATE DATABASE outside of a transaction block
conn.autocommit = True

# Create a cursor object
cursor = conn.cursor()

# Create the "nutrition" database if it doesn't exist
cursor.execute('''SELECT 1 FROM pg_database WHERE datname = 'nutrition' ''')
if cursor.fetchone() is None:
    cursor.execute("CREATE DATABASE \"nutrition\"")
    print("Database 'nutrition' created successfully.")

# Close the cursor and connection
cursor.close()
conn.close()