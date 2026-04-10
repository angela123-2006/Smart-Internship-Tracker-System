"""
==============================================================
Smart Internship Tracker System — Skill Model
==============================================================
Handles database operations for student skills and proficiency.
==============================================================
"""

from mysql.connector import Error
from database.db_connection import get_db_connection

VALID_PROFICIENCY_LEVELS = {"Beginner", "Intermediate", "Advanced"}


def add_skill(student_id, skill_name, proficiency_level):
    """
    Add a skill entry for a student.

    Args:
        student_id (int): FK to Students.
        skill_name (str): e.g. "Python", "SQL".
        proficiency_level (str): "Beginner" | "Intermediate" | "Advanced".

    Returns:
        dict: Success status and skill ID, or error.
    """
    if proficiency_level not in VALID_PROFICIENCY_LEVELS:
        return {
            "success": False,
            "error": (
                f"Invalid proficiency level. "
                f"Must be one of: {VALID_PROFICIENCY_LEVELS}"
            ),
        }

    connection = get_db_connection()
    if connection is None:
        return {"success": False, "error": "Database connection failed"}

    try:
        cursor = connection.cursor()
        query = """
            INSERT INTO Skills (Student_ID, Skill_Name, Proficiency_Level)
            VALUES (%s, %s, %s)
        """
        cursor.execute(query, (student_id, skill_name, proficiency_level))
        connection.commit()

        return {"success": True, "skill_id": cursor.lastrowid}

    except Error as err:
        if err.errno == 1062:
            return {
                "success": False,
                "error": "This skill already exists for the student",
            }
        return {"success": False, "error": str(err)}

    finally:
        cursor.close()
        connection.close()


def get_student_skills(student_id):
    """
    Retrieve all skills for a given student.

    Args:
        student_id (int): The student's primary key.

    Returns:
        list[dict]: Skill records for that student.
    """
    connection = get_db_connection()
    if connection is None:
        return []

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT * FROM Skills WHERE Student_ID = %s ORDER BY Skill_Name",
            (student_id,),
        )
        return cursor.fetchall()

    except Error as err:
        print(f"[MODEL ERROR] get_student_skills: {err}")
        return []

    finally:
        cursor.close()
        connection.close()
