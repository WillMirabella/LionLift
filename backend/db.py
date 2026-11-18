import psycopg2
import random

# This method establishes a connection with a postgres server
# It is currently configured to connect to a server on your local machine
# You MUST have a database running for it to work
#
# I included a guide below
# https://www.w3schools.com/postgresql/postgresql_install.php
#
# Eventually, we can reconfigure this for a remote server
def get_connection():
    try:
        return psycopg2.connect(
            database="postgres",
            user="postgres",
            password="password",
            host="127.0.0.1",
            port=5432,
        )
        print("Connection to PostgreSQL established successfully.")
    except:
        print("Connection to PostgreSQL failed.")
        return False

# Creates relations, if they don't already exist
def create_relations():
    query = """
        CREATE TABLE IF NOT EXISTS cars (
            id SERIAL PRIMARY KEY,
            make VARCHAR(100),
            model VARCHAR(100),
            color VARCHAR(100),
            year INTEGER,
            capacity INTEGER
        );
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(100),
            password VARCHAR(100),
            first_name VARCHAR(100),
            last_name VARCHAR(100),
            phone VARCHAR(100),
            gender VARCHAR(100),
            description VARCHAR(100),
            grad_year INTEGER,
            major VARCHAR(100),
            schedule VARCHAR(100),
            street VARCHAR(100),
            city VARCHAR(100),
            state VARCHAR(100),
            zip VARCHAR(100),
            latitude VARCHAR(100),
            longitude VARCHAR(100),
            preferred_payment VARCHAR(100),
            car_id INTEGER REFERENCES cars(id)
        );
        CREATE TABLE IF NOT EXISTS contacts (
            id SERIAL PRIMARY KEY,
            sender INTEGER REFERENCES users(id),
            receiver INTEGER REFERENCES users(id),
            method VARCHAR(100),
            datetime VARCHAR(100)
        );
        CREATE TABLE IF NOT EXISTS email_verifications (
            email VARCHAR(254) PRIMARY KEY,
            code_hash CHAR(64),
            expires_at TIMESTAMPTZ,
            attempts INTEGER NOT NULL DEFAULT 0,
            last_sent_at TIMESTAMPTZ,
            verified BOOLEAN NOT NULL DEFAULT FALSE
        );
        CREATE TABLE IF NOT EXISTS password_resets (
            email VARCHAR(254) PRIMARY KEY,
            code_hash CHAR(64),
            expires_at TIMESTAMPTZ,
            attempts INTEGER NOT NULL DEFAULT 0,
            last_sent_at TIMESTAMPTZ,
            token_id VARCHAR(64)
        );
    """
    conn = get_connection()
    curr = conn.cursor()
    curr.execute(query)
    conn.commit()
    conn.close()

# Deletes all relations, use with caution
def clear_relations():
    query = """
        DROP SCHEMA public CASCADE;
        CREATE SCHEMA public;
    """
    conn = get_connection()
    curr = conn.cursor()
    curr.execute(query)
    conn.commit()
    conn.close()

# Inserts a new user into the users relation and returns the new user_id
def insert_user(u):
    query = """
        INSERT INTO users (
            email, password, first_name, last_name, phone, gender,
            description, grad_year, major, street, city, state, zip,
            longitude, latitude, schedule, preferred_payment, car_id
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id;
    """
    new_user_data = (
        u.email, u.password, u.first_name, u.last_name, u.phone, u.gender,
        u.description, u.grad_year, u.major, u.street, u.city, u.state, u.zip,
        u.longitude, u.latitude, u.schedule, u.preferred_payment, u.car_id
    )
    conn = get_connection()
    curr = conn.cursor()
    curr.execute(query,new_user_data)
    conn.commit()
    new_id=curr.fetchone()[0]
    conn.close()

    return new_id

# Updates a row of the user relation
def update_user(u):
    query = """
        INSERT INTO users (
            email, password, first_name, last_name, phone, gender,
            description, grad_year, major, street, city, state, zip,
            longitude, latitude, schedule, preferred_payment, car_id
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id;
    """
    new_user_data = (
        u.first_name, u.last_name, u.phone, u.email, u.gender,
        u.description, u.grad_year, u.major, u.street, u.city, u.state,
        u.zip, u.longitude, u.latitude, u.schedule, u.preferred_payment,
        u.car_id, u.id
    )
    conn = get_connection()
    curr = conn.cursor()
    curr.execute(query,new_user_data)
    conn.commit()
    conn.close()

# Returns the data of the row in users with the specified id
def get_user_by_id(id):
    query = """
            SELECT * 
            FROM users 
            WHERE id =  %s;
        """
    conn = get_connection()
    curr = conn.cursor()
    curr.execute(query,(id,))
    row = curr.fetchone()
    conn.close()

    return row

# Returns the data of the row in users with the specified email
def get_user_by_email(email):
    query = """
            SELECT * 
            FROM users 
            WHERE email =  %s;
        """
    conn = get_connection()
    curr = conn.cursor()
    curr.execute(query,(email,))
    row = curr.fetchone()
    conn.close()

    return row


# Returns every user's locations
def get_users_locations():
    query = """
            SELECT latitude, longitude
            FROM users 
        """
    conn = get_connection()
    curr = conn.cursor()
    curr.execute(query)
    rows = curr.fetchall()
    conn.close()

    # Randomize location by about a mile
    offset = 0.015

    return [
        (
            round(float(lat) + random.uniform(-offset, offset), 5),
            round(float(lng) + random.uniform(-offset, offset), 5),
        )
        for lat, lng in rows
        if lat is not None and lng is not None
    ]

# Inserts a new car into the cars relation and returns the new id
def insert_car(c):
    query = """
        INSERT INTO cars (make, model, color, year, capacity) 
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id, make, model, color, year, capacity;
    """
    new_car_data= (c.make, c.model, c.color, c.year, c.capacity)

    conn = get_connection()
    curr = conn.cursor()
    curr.execute(query,new_car_data)
    conn.commit()
    new_id=curr.fetchone()[0]
    conn.close()
    return new_id

# Updates a row of the user relation
def update_car(c):
    query = """
        UPDATE cars
        SET make = %s, model = %s, color = %s, year = %s, capacity = %s
        WHERE id = %s;
    """
    new_car_data= (c.make, c.model, c.color, c.year, c.capacity, c.id)

    conn = get_connection()
    curr = conn.cursor()
    curr.execute(query,new_car_data)
    conn.commit()
    conn.close()

# Returns the data of the row in cars with the specified id
def get_car_by_id(id):
    query = """
            SELECT * 
            FROM cars 
            WHERE id = %s;
        """
    conn = get_connection()
    curr = conn.cursor()
    curr.execute(query,(id,))
    row = curr.fetchone()
    conn.close()

    return row

# Inserts a new contact into the contacts relation and returns the new id
def insert_contact(sender, receiver, method, datetime):
    query = """
        INSERT INTO contacts (sender, receiver, method, datetime) 
        VALUES (%s, %s, %s, %s)
        RETURNING id, sender, receiver, method
    """
    new_contact_data = (sender, receiver, method, datetime)

    conn = get_connection()
    curr = conn.cursor()
    curr.execute(query,new_contact_data)
    conn.commit()
    new_id=curr.fetchone()[0]
    conn.close()
    return new_id

# Returns the data of the row in contacts with the specified id
def get_contact_by_id(id):
    query = """
            SELECT * 
            FROM contacts 
            WHERE id = %s;
        """
    conn = get_connection()
    curr = conn.cursor()
    curr.execute(query,(id,))
    row = curr.fetchone()
    conn.close()

    return row
# Saves a new verification code for an email, replacing any older code
# The actual code is never stored, only its hash
def save_verification_code(email, code_hash, expires_at):
    query = """
        INSERT INTO email_verifications (email, code_hash, expires_at, attempts, last_sent_at)
        VALUES (%s, %s, %s, 0, NOW())
        ON CONFLICT (email) DO UPDATE
        SET code_hash = EXCLUDED.code_hash, expires_at = EXCLUDED.expires_at, attempts = 0, last_sent_at = NOW();
    """
    conn = get_connection()
    curr = conn.cursor()
    curr.execute(query,(email, code_hash, expires_at))
    conn.commit()
    conn.close()

# Returns (code_hash, expires_at, attempts, last_sent_at, verified) for an email, or None
def get_verification(email):
    query = """
            SELECT code_hash, expires_at, attempts, last_sent_at, verified
            FROM email_verifications
            WHERE email = %s;
        """
    conn = get_connection()
    curr = conn.cursor()
    curr.execute(query,(email,))
    row = curr.fetchone()
    conn.close()

    return row

# Counts a wrong guess against an email's current code
def increment_verification_attempts(email):
    query = """
        UPDATE email_verifications
        SET attempts = attempts + 1
        WHERE email = %s;
    """
    conn = get_connection()
    curr = conn.cursor()
    curr.execute(query,(email,))
    conn.commit()
    conn.close()

# Marks an email as verified and clears its code so it can't be reused
def mark_email_verified(email):
    query = """
        UPDATE email_verifications
        SET verified = TRUE, code_hash = NULL, expires_at = NULL
        WHERE email = %s;
    """
    conn = get_connection()
    curr = conn.cursor()
    curr.execute(query,(email,))
    conn.commit()
    conn.close()

# Returns True if the email has been verified
# Use this to block unverified users from other endpoints
def is_email_verified(email):
    row = get_verification(email)
    return row is not None and row[4]


# Saves a new password reset code for an email, replacing any older code or reset token
# The actual code is never stored, only its hash
def save_reset_code(email, code_hash, expires_at):
    query = """
        INSERT INTO password_resets (email, code_hash, expires_at, attempts, last_sent_at, token_id)
        VALUES (%s, %s, %s, 0, NOW(), NULL)
        ON CONFLICT (email) DO UPDATE
        SET code_hash = EXCLUDED.code_hash, expires_at = EXCLUDED.expires_at, attempts = 0,
            last_sent_at = NOW(), token_id = NULL;
    """
    conn = get_connection()
    curr = conn.cursor()
    curr.execute(query,(email, code_hash, expires_at))
    conn.commit()
    conn.close()

# Returns (code_hash, expires_at, attempts, last_sent_at, token_id) for an email, or None
def get_reset(email):
    query = """
            SELECT code_hash, expires_at, attempts, last_sent_at, token_id
            FROM password_resets
            WHERE email = %s;
        """
    conn = get_connection()
    curr = conn.cursor()
    curr.execute(query,(email,))
    row = curr.fetchone()
    conn.close()

    return row

# Counts a wrong guess against an email's current reset code
def increment_reset_attempts(email):
    query = """
        UPDATE password_resets
        SET attempts = attempts + 1
        WHERE email = %s;
    """
    conn = get_connection()
    curr = conn.cursor()
    curr.execute(query,(email,))
    conn.commit()
    conn.close()

# Clears the reset code once it's used, and remembers the id of the reset token handed out
# so that token can only be used once
def mark_reset_code_used(email, token_id):
    query = """
        UPDATE password_resets
        SET code_hash = NULL, expires_at = NULL, token_id = %s
        WHERE email = %s;
    """
    conn = get_connection()
    curr = conn.cursor()
    curr.execute(query,(token_id, email))
    conn.commit()
    conn.close()

# Sets a user's new password and uses up the reset token in one transaction
# Only succeeds if token_id is still the current reset token for that email
# Returns True if the password was changed
def reset_password(email, token_id, password_hash):
    conn = get_connection()
    curr = conn.cursor()
    curr.execute(
        "UPDATE password_resets SET token_id = NULL WHERE email = %s AND token_id = %s;",
        (email, token_id),
    )
    if curr.rowcount != 1:
        conn.rollback()
        conn.close()
        return False
    curr.execute("UPDATE users SET password = %s WHERE email = %s;", (password_hash, email))
    changed = curr.rowcount == 1
    if changed:
        conn.commit()
    else:
        conn.rollback()
    conn.close()
    return changed
