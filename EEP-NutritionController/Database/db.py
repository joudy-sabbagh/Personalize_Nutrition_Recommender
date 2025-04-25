# database/db.py

import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

def get_connection():
    """
    Establish a connection to the PostgreSQL database using environment variables.
    """
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=os.getenv("DB_PORT")
    )
    return conn

def create_tables():
    """
    Create all necessary tables in the PostgreSQL database.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # Create the "User Profile" table
    cursor.execute('''CREATE TABLE IF NOT EXISTS user_profile (
                        user_id SERIAL PRIMARY KEY,
                        username VARCHAR(255) UNIQUE NOT NULL,
                        password VARCHAR(255) NOT NULL,
                        email VARCHAR(255) UNIQUE NOT NULL);''')

    # Create the "Meal Log" table
    cursor.execute('''CREATE TABLE IF NOT EXISTS meal_log (
                        user_id INTEGER REFERENCES user_profile(user_id),
                        meal_id SERIAL PRIMARY KEY,
                        protein_pct FLOAT,
                        carbs_pct FLOAT,
                        fat_pct FLOAT,
                        sugar_risk VARCHAR(50),
                        refined_carb BOOLEAN,
                        meal_category VARCHAR(100),
                        glucose_spike_30min FLOAT,
                        glucose_spike_60min FLOAT,
                        FOREIGN KEY (user_id) REFERENCES user_profile(user_id));''')

    # Create the "Microbiome Data" table
    cursor.execute('''CREATE TABLE IF NOT EXISTS microbiome_data (
                        user_id INTEGER REFERENCES user_profile(user_id),
                        bact_id SERIAL PRIMARY KEY,
                        bact_test VARCHAR(255),
                        FOREIGN KEY (user_id) REFERENCES user_profile(user_id));''')

    # Create the "Clinical User Data" table
    cursor.execute('''CREATE TABLE IF NOT EXISTS clinical_user_data (
                        user_id INTEGER REFERENCES user_profile(user_id),
                        clinical_age INTEGER,
                        clinical_weight FLOAT,
                        clinical_height FLOAT,
                        clinical_bmi FLOAT,
                        clinical_fasting_glucose FLOAT,
                        clinical_fasting_insulin FLOAT,
                        clinical_hba1c FLOAT,
                        clinical_homa_ir FLOAT,
                        clinical_gender CHAR(1),
                        FOREIGN KEY (user_id) REFERENCES user_profile(user_id));''')

    # Commit the changes
    conn.commit()

    # Close the cursor and connection
    cursor.close()
    conn.close()

    print("Tables created successfully.")

def main():
    """
    Main function to create tables in the PostgreSQL database.
    """
    create_tables()

if __name__ == "__main__":
    main()