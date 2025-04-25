# database/db.py

import psycopg2
from psycopg2 import sql
from dotenv import load_dotenv
import os
import bcrypt

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
                        bact_test TEXT,
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

def hash_password(password):
    """
    Hash a password using bcrypt.
    """
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def check_password(plain_password, hashed_password):
    """
    Verify a password against a hash.
    """
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def user_signup(username, email, password):
    """
    Register a new user in the database.
    Returns user_id if successful, None if username/email already exists.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Check if username already exists
        cursor.execute("SELECT 1 FROM user_profile WHERE username = %s", (username,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return None, "Username already exists"
        
        # Check if email already exists
        cursor.execute("SELECT 1 FROM user_profile WHERE email = %s", (email,))
        if cursor.fetchone():
            cursor.close()
            conn.close()
            return None, "Email already exists"
        
        # Hash the password
        hashed_password = hash_password(password)
        
        # Insert the new user
        cursor.execute(
            "INSERT INTO user_profile (username, email, password) VALUES (%s, %s, %s) RETURNING user_id",
            (username, email, hashed_password)
        )
        
        user_id = cursor.fetchone()[0]
        conn.commit()
        
        return user_id, "User created successfully"
    
    except Exception as e:
        conn.rollback()
        return None, str(e)
    
    finally:
        cursor.close()
        conn.close()

def user_signin(username, password):
    """
    Authenticate a user by username and password.
    Returns user data if successful, None otherwise.
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Get user by username
        cursor.execute(
            "SELECT user_id, username, password, email FROM user_profile WHERE username = %s",
            (username,)
        )
        
        user = cursor.fetchone()
        if not user:
            return None, "Invalid username"
        
        # Verify password
        user_id, username, hashed_password, email = user
        if check_password(password, hashed_password):
            return {
                "user_id": user_id,
                "username": username,
                "email": email
            }, "Login successful"
        else:
            return None, "Invalid password"
    
    except Exception as e:
        return None, str(e)
    
    finally:
        cursor.close()
        conn.close()

def save_bacteria_data(user_id, bacteria_string):
    """
    Save the bacteria data string for a user.
    The string contains 0s and 1s indicating presence (1) or absence (0) of different bacteria.
    
    Args:
        user_id (int): The user ID
        bacteria_string (str): A string of 0s and 1s representing bacteria presence
        
    Returns:
        tuple: (bact_id, message) - bact_id if successful, None if failed
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Insert the bacteria data
        cursor.execute(
            "INSERT INTO microbiome_data (user_id, bact_test) VALUES (%s, %s) RETURNING bact_id",
            (user_id, bacteria_string)
        )
        
        bact_id = cursor.fetchone()[0]
        conn.commit()
        
        return bact_id, "Bacteria data saved successfully"
    
    except Exception as e:
        conn.rollback()
        return None, str(e)
    
    finally:
        cursor.close()
        conn.close()