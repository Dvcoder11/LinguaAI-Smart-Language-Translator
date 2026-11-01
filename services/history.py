
# ==========================================
# LINGUAAI - DATABASE MANAGEMENT
# Users + Translation History
# ==========================================

import sqlite3
from datetime import datetime

DATABASE_NAME = "linguaai.db"


# ==========================================
# 1. DATABASE CONNECTION
# ==========================================

def get_connection():

    connection = sqlite3.connect(DATABASE_NAME)
    connection.row_factory = sqlite3.Row

    return connection


# ==========================================
# 2. INITIALIZE DATABASE
# ==========================================

def initialize_database():

    connection = get_connection()
    cursor = connection.cursor()

    # Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    # Existing history table (preserves old databases)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS translation_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_text TEXT NOT NULL,
            translated_text TEXT NOT NULL,
            source_language TEXT NOT NULL,
            target_language TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    # Check whether user_id already exists
    cursor.execute("PRAGMA table_info(translation_history)")

    columns = [
        column["name"]
        for column in cursor.fetchall()
    ]

    if "user_id" not in columns:

        cursor.execute("""
            ALTER TABLE translation_history
            ADD COLUMN user_id INTEGER REFERENCES users(id)
        """)

    cursor.execute("""
        CREATE INDEX IF NOT EXISTS
        idx_history_user_id
        ON translation_history(user_id)
    """)

    connection.commit()
    connection.close()


# ==========================================
# 3. CREATE USER
# ==========================================

def create_user(username, email, password_hash):

    connection = get_connection()
    cursor = connection.cursor()

    try:

        created_at = datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        cursor.execute("""
            INSERT INTO users (
                username,
                email,
                password_hash,
                created_at
            )
            VALUES (?, ?, ?, ?)
        """, (
            username,
            email,
            password_hash,
            created_at
        ))

        user_id = cursor.lastrowid

        # Transfer old unassigned history to the first account.
        cursor.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]

        if user_count == 1:

            cursor.execute("""
                UPDATE translation_history
                SET user_id = ?
                WHERE user_id IS NULL
            """, (user_id,))

        connection.commit()

        return user_id

    except sqlite3.IntegrityError:

        connection.rollback()
        return None

    finally:

        connection.close()


# ==========================================
# 4. FIND USER BY EMAIL
# ==========================================

def get_user_by_email(email):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM users
        WHERE email = ?
    """, (email,))

    user = cursor.fetchone()

    connection.close()

    return dict(user) if user else None


# ==========================================
# 5. FIND USER BY ID
# ==========================================

def get_user_by_id(user_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, username, email, created_at
        FROM users
        WHERE id = ?
    """, (user_id,))

    user = cursor.fetchone()

    connection.close()

    return dict(user) if user else None


# ==========================================
# 6. SAVE TRANSLATION
# ==========================================

def save_translation(
    original_text,
    translated_text,
    source_language,
    target_language,
    user_id
):

    connection = get_connection()
    cursor = connection.cursor()

    created_at = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    cursor.execute("""
        INSERT INTO translation_history (
            original_text,
            translated_text,
            source_language,
            target_language,
            created_at,
            user_id
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        original_text,
        translated_text,
        source_language,
        target_language,
        created_at,
        user_id
    ))

    connection.commit()
    connection.close()


# ==========================================
# 7. GET USER'S TRANSLATION HISTORY
# ==========================================

def get_translation_history(user_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT *
        FROM translation_history
        WHERE user_id = ?
        ORDER BY id DESC
    """, (user_id,))

    history = [
        dict(row) for row in cursor.fetchall()
    ]

    connection.close()

    return history


# ==========================================
# 8. DELETE USER'S TRANSLATION HISTORY
# ==========================================

def delete_all_history(user_id):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM translation_history
        WHERE user_id = ?
    """, (user_id,))

    connection.commit()
    connection.close()
