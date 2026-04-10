"""
==============================================================
Smart Internship Tracker System — Student Model
==============================================================
Handles all database operations related to Students.
Uses parameterized queries to prevent SQL injection.
==============================================================
"""

from mysql.connector import Error
from database.db_connection import get_db_connection


def create_student(name, email, department, cgpa):
    """
    Insert a new student into the database.

    Args:
        name (str): Full name of the student.
        email (str): Email address (must be unique).
        department (str): Academic department.
        cgpa (float): Cumulative GPA (0.00 – 10.00).

    Returns:
        dict: {"success": True, "student_id": <id>} on success,
              {"success": False, "error": "<message>"} on failure.
    """
    connection = get_db_connection()
    if connection is None:
        return {"success": False, "error": "Database connection failed"}

    try:
        cursor = connection.cursor()
        query = """
            INSERT INTO Students (Name, Email, Department, CGPA)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (name, email, department, cgpa))
        connection.commit()

        return {"success": True, "student_id": cursor.lastrowid}

    except Error as err:
        return {"success": False, "error": str(err)}

    finally:
        cursor.close()
        connection.close()


def get_all_students():
    """
    Retrieve all students from the database.

    Returns:
        list[dict]: A list of student records.
    """
    connection = get_db_connection()
    if connection is None:
        return []

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Students ORDER BY Name")
        students = cursor.fetchall()
        return students

    except Error as err:
        print(f"[MODEL ERROR] get_all_students: {err}")
        return []

    finally:
        cursor.close()
        connection.close()


def get_student_by_id(student_id):
    """
    Retrieve a single student by their ID.

    Args:
        student_id (int): The student's primary key.

    Returns:
        dict | None: The student record, or None if not found.
    """
    connection = get_db_connection()
    if connection is None:
        return None

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM Students WHERE Student_ID = %s",
            (student_id,),
        )
        student = cursor.fetchone()
        return student

    except Error as err:
        print(f"[MODEL ERROR] get_student_by_id: {err}")
        return None

    finally:
        cursor.close()
        connection.close()
