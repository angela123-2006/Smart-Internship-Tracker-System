"""
==============================================================
Smart Internship Tracker System — Company Model
==============================================================
Handles all database operations related to Companies.
==============================================================
"""

from mysql.connector import Error
from database.db_connection import get_db_connection


def create_company(company_name, location, industry_type, website=None):
    """
    Insert a new company into the database.

    Args:
        company_name (str): Name of the company.
        location (str): City / office location.
        industry_type (str): e.g. "Software", "FinTech".
        website (str | None): Company URL (optional).

    Returns:
        dict: Success status and new company ID, or error message.
    """
    connection = get_db_connection()
    if connection is None:
        return {"success": False, "error": "Database connection failed"}

    try:
        cursor = connection.cursor()
        query = """
            INSERT INTO Companies (Company_Name, Location, Industry_Type, Website)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (company_name, location, industry_type, website))
        connection.commit()

        return {"success": True, "company_id": cursor.lastrowid}

    except Error as err:
        return {"success": False, "error": str(err)}

    finally:
        cursor.close()
        connection.close()


def get_all_companies():
    """
    Retrieve all companies ordered by name.

    Returns:
        list[dict]: A list of company records.
    """
    connection = get_db_connection()
    if connection is None:
        return []

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Companies ORDER BY Company_Name")
        return cursor.fetchall()

    except Error as err:
        print(f"[MODEL ERROR] get_all_companies: {err}")
        return []

    finally:
        cursor.close()
        connection.close()
