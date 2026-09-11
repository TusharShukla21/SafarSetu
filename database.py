import sqlite3
import os

from config import Config


# =========================================================
# DATABASE CONNECTION
# =========================================================

def get_db_connection():
    """
    Creates and returns a SQLite database connection.
    """

    connection = sqlite3.connect(
        Config.DATABASE
    )

    # Allows us to access columns by name
    # Example:
    # user["name"]
    # instead of:
    # user[1]

    connection.row_factory = sqlite3.Row

    # Enable foreign key support
    connection.execute(
        "PRAGMA foreign_keys = ON"
    )

    return connection


# =========================================================
# INITIALIZE DATABASE
# =========================================================

def init_database():
    """
    Creates all database tables using schema.sql.
    """

    schema_path = os.path.join(
        os.path.dirname(__file__),
        "schema.sql"
    )

    connection = get_db_connection()

    try:

        with open(
            schema_path,
            "r",
            encoding="utf-8"
        ) as schema_file:

            schema = schema_file.read()

        connection.executescript(
            schema
        )

        connection.commit()

        print(
            "Database initialized successfully."
        )

    except Exception as error:

        connection.rollback()

        print(
            "Database initialization failed:"
        )

        print(error)

        raise

    finally:

        connection.close()


# =========================================================
# CLOSE DATABASE
# =========================================================

def close_connection(connection):
    """
    Safely closes a database connection.
    """

    if connection:

        connection.close()