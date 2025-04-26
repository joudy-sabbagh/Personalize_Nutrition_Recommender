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
                        sugar_risk INTEGER,
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

def save_clinical_data(user_id, clinical_data):
    """
    Save the clinical data for a user.
    
    Args:
        user_id (int): The user ID
        clinical_data (dict): Dictionary containing clinical data fields
        
    Returns:
        tuple: (success, message) - True if successful, False if failed
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Check if user already has clinical data
        cursor.execute("SELECT 1 FROM clinical_user_data WHERE user_id = %s", (user_id,))
        user_exists = cursor.fetchone()
        
        if user_exists:
            # Update existing record
            update_query = """
            UPDATE clinical_user_data SET 
                clinical_age = %s,
                clinical_weight = %s,
                clinical_height = %s,
                clinical_bmi = %s,
                clinical_fasting_glucose = %s,
                clinical_fasting_insulin = %s,
                clinical_hba1c = %s,
                clinical_homa_ir = %s,
                clinical_gender = %s
            WHERE user_id = %s
            """
            cursor.execute(update_query, (
                clinical_data.get('clinical_age'),
                clinical_data.get('clinical_weight'),
                clinical_data.get('clinical_height'),
                clinical_data.get('clinical_bmi'),
                clinical_data.get('clinical_fasting_glucose'),
                clinical_data.get('clinical_fasting_insulin'),
                clinical_data.get('clinical_hba1c'),
                clinical_data.get('clinical_homa_ir'),
                clinical_data.get('clinical_gender'),
                user_id
            ))
        else:
            # Insert new record
            insert_query = """
            INSERT INTO clinical_user_data (
                user_id, 
                clinical_age, 
                clinical_weight, 
                clinical_height, 
                clinical_bmi, 
                clinical_fasting_glucose, 
                clinical_fasting_insulin, 
                clinical_hba1c, 
                clinical_homa_ir, 
                clinical_gender
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (
                user_id,
                clinical_data.get('clinical_age'),
                clinical_data.get('clinical_weight'),
                clinical_data.get('clinical_height'),
                clinical_data.get('clinical_bmi'),
                clinical_data.get('clinical_fasting_glucose'),
                clinical_data.get('clinical_fasting_insulin'),
                clinical_data.get('clinical_hba1c'),
                clinical_data.get('clinical_homa_ir'),
                clinical_data.get('clinical_gender')
            ))
        
        conn.commit()
        return True, "Clinical data saved successfully"
    
    except Exception as e:
        conn.rollback()
        return False, str(e)
    
    finally:
        cursor.close()
        conn.close()

def save_meal_data(user_id, meal_data):
    """
    Save meal log data for a user.
    
    Args:
        user_id (int): The user ID
        meal_data (dict): Dictionary containing meal data fields
        
    Returns:
        tuple: (meal_id, message) - meal_id if successful, None if failed
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        # Insert the meal data
        insert_query = """
        INSERT INTO meal_log (
            user_id,
            protein_pct,
            carbs_pct,
            fat_pct,
            sugar_risk,
            refined_carb,
            meal_category,
            glucose_spike_30min,
            glucose_spike_60min
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING meal_id
        """
        
        cursor.execute(insert_query, (
            user_id,
            meal_data.get('protein_pct'),
            meal_data.get('carbs_pct'),
            meal_data.get('fat_pct'),
            meal_data.get('sugar_risk'),
            meal_data.get('refined_carb'),
            meal_data.get('meal_category'),
            meal_data.get('glucose_spike_30min'),
            meal_data.get('glucose_spike_60min')
        ))
        
        meal_id = cursor.fetchone()[0]
        conn.commit()
        
        return meal_id, "Meal data saved successfully"
    
    except Exception as e:
        conn.rollback()
        return None, str(e)
    
    finally:
        cursor.close()
        conn.close()

def get_user_clinical_data(user_id):
    """
    Retrieve clinical data for a user.
    
    Args:
        user_id (int): The user ID
        
    Returns:
        dict: User's clinical data or None if not found
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT 
                clinical_age,
                clinical_weight,
                clinical_height,
                clinical_bmi,
                clinical_fasting_glucose,
                clinical_fasting_insulin,
                clinical_hba1c,
                clinical_homa_ir,
                clinical_gender
            FROM clinical_user_data 
            WHERE user_id = %s
        """, (user_id,))
        
        result = cursor.fetchone()
        if not result:
            return None
            
        return {
            "clinical_age": result[0],
            "clinical_weight": result[1],
            "clinical_height": result[2],
            "clinical_bmi": result[3],
            "clinical_fasting_glucose": result[4],
            "clinical_fasting_insulin": result[5],
            "clinical_hba1c": result[6],
            "clinical_homa_ir": result[7],
            "clinical_gender": result[8]
        }
    
    except Exception as e:
        print(f"Error retrieving clinical data: {str(e)}")
        return None
    
    finally:
        cursor.close()
        conn.close()

def get_user_microbiome_data(user_id):
    """
    Retrieve the latest microbiome data for a user.
    
    Args:
        user_id (int): The user ID
        
    Returns:
        tuple: (bact_id, bact_test) or (None, None) if not found
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        cursor.execute("""
            SELECT bact_id, bact_test
            FROM microbiome_data 
            WHERE user_id = %s
            ORDER BY bact_id DESC
            LIMIT 1
        """, (user_id,))
        
        result = cursor.fetchone()
        if not result:
            return None, None
            
        return result[0], result[1]
    
    except Exception as e:
        print(f"Error retrieving microbiome data: {str(e)}")
        return None, None
    
    finally:
        cursor.close()
        conn.close()