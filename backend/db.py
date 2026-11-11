import os
import psycopg2
from psycopg2.extras import Json


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
        conn = psycopg2.connect(
            database=os.getenv("PGDATABASE", "lionlift_dev"),
            user=os.getenv("PGUSER", "postgres"),
            password=os.getenv("PGPASSWORD"),
            host=os.getenv("PGHOST", "127.0.0.1"),
            port=os.getenv("PGPORT", "5432"),
        )
        print("Connection to PostgreSQL established successfully.")
        return conn

    except psycopg2.OperationalError as error:
        print(f"Connection to PostgreSQL failed: {error}")
        return False

# Creates relations, if they don't already exist

def create_relations():
    query = """
        CREATE TABLE IF NOT EXISTS cars (
            id SERIAL PRIMARY KEY,
            make VARCHAR(100),
            model VARCHAR(100),
            color VARCHAR(50),
            year INTEGER,
            capacity SMALLINT
        );

        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            first_name VARCHAR(100),
            last_name VARCHAR(100),
            phone VARCHAR(20),
            email VARCHAR(254),
            gender VARCHAR(50),
            description TEXT,
            grad_year INTEGER,
            major VARCHAR(100),
            schedule JSONB,
            address TEXT,
            preferred_payment VARCHAR(50),
            car_id INTEGER REFERENCES cars(id)
        );

        CREATE TABLE IF NOT EXISTS contacts (
            id SERIAL PRIMARY KEY,
            sender INTEGER REFERENCES users(id),
            receiver INTEGER REFERENCES users(id),
            method VARCHAR(50),
            datetime TIMESTAMPTZ
        );

        CREATE TABLE IF NOT EXISTS email_verifications (
            email VARCHAR(254) PRIMARY KEY,
            code_hash CHAR(64),
            expires_at TIMESTAMPTZ,
            attempts INTEGER NOT NULL DEFAULT 0,
            last_sent_at TIMESTAMPTZ,
            verified BOOLEAN NOT NULL DEFAULT FALSE
        );
    """

    conn = get_connection()
    curr = conn.cursor()
    curr.execute(query)
    conn.commit()
    curr.close()
    conn.close()

# Deletes all relations. Use with caution.
def clear_relations():
    query = """
        DROP SCHEMA public CASCADE;
        CREATE SCHEMA public;
    """
    conn = get_connection()
    curr = conn.cursor()
    curr.execute(query)
    conn.commit()
    curr.close()
    conn.close()

# Inserts a new user into the users relation and returns the new user_id
def insert_user(u):
    query = """
        INSERT INTO users (
            first_name, last_name, phone, email, gender,
            description, grad_year, major, address,
            preferred_payment, schedule
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        RETURNING id;
    """
    new_user_data = (
        u.first_name,
        u.last_name,
        u.phone,
        u.email,
        u.gender,
        u.description,
        u.grad_year,
        u.major,
        u.address,
        u.preferred_payment,
        Json(u.schedule)
    )
    conn = get_connection()
    curr = conn.cursor()
    curr.execute(query, new_user_data)
    conn.commit()

    new_id = curr.fetchone()[0]

    curr.close()
    conn.close()

    return new_id

# Updates a row of the user relation
def update_user(u):
    query = """
        UPDATE users
        SET
            first_name = %s,
            last_name = %s,
            phone = %s,
            email = %s,
            gender = %s,
            description = %s,
            grad_year = %s,
            major = %s,
            schedule = %s,
            address = %s,
            preferred_payment = %s,
            car_id = %s
        WHERE id = %s;
    """

    new_user_data = (
        u.first_name,
        u.last_name,
        u.phone,
        u.email,
        u.gender,
        u.description,
        u.grad_year,
        u.major,
        Json(u.schedule),
        u.address,
        u.preferred_payment,
        u.car_id,
        u.id
    )

    conn = get_connection()
    curr = conn.cursor()
    curr.execute(query, new_user_data)
    conn.commit()
    curr.close()
    conn.close()

# Returns the data of the row in users with the specified id
def get_user_by_id(id):
    query = """
        SELECT
            id, first_name, last_name, phone, email,
            gender, description, grad_year, major,
            schedule, address, preferred_payment, car_id
        FROM users
        WHERE id = %s;
    """

    conn = get_connection()
    curr = conn.cursor()
    curr.execute(query, (id,))
    row = curr.fetchone()

    curr.close()
    conn.close()

    return row

# Inserts a new car into the cars relation and returns the new id
def insert_car(c):
    query = """
        INSERT INTO cars (make, model, color, year, capacity)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id;
    """

    new_car_data = (c.make, c.model, c.color, c.year, c.capacity)

    conn = get_connection()
    curr = conn.cursor()
    curr.execute(query, new_car_data)
    conn.commit()

    new_id = curr.fetchone()[0]

    curr.close()
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
        SELECT id, make, model, color, year, capacity
        FROM cars
        WHERE id = %s;
    """

    conn = get_connection()
    curr = conn.cursor()
    curr.execute(query, (id,))
    row = curr.fetchone()

    curr.close()
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
        SELECT id, sender, receiver, method, datetime
        FROM contacts
        WHERE id = %s;
    """

    conn = get_connection()
    curr = conn.cursor()
    curr.execute(query, (id,))
    row = curr.fetchone()

    curr.close()
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
    curr.close()
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
