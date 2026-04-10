"""
==============================================================
Smart Internship Tracker System — Internship Model
==============================================================
Handles all database operations related to Internships,
including a simple skill-matching recommendation engine.
==============================================================
"""

from mysql.connector import Error
from database.db_connection import get_db_connection


def create_internship(company_id, role, required_skills, duration,
                      stipend, application_deadline):
    """
    Insert a new internship posting.

    Args:
        company_id (int): FK to Companies table.
        role (str): Job title / role.
        required_skills (str): Comma-separated skill names.
        duration (str): e.g. "3 months".
        stipend (float): Monthly stipend amount.
        application_deadline (str): Date string "YYYY-MM-DD".

    Returns:
        dict: Success status with internship ID, or error.
    """
    connection = get_db_connection()
    if connection is None:
        return {"success": False, "error": "Database connection failed"}

    try:
        cursor = connection.cursor()
        query = """
            INSERT INTO Internships
                (Company_ID, Role, Required_Skills, Duration,
                 Stipend, Application_Deadline)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            company_id, role, required_skills,
            duration, stipend, application_deadline,
        ))
        connection.commit()

        return {"success": True, "internship_id": cursor.lastrowid}

    except Error as err:
        return {"success": False, "error": str(err)}

    finally:
        cursor.close()
        connection.close()


def get_all_internships():
    """
    Retrieve all internships with their company details.

    Returns:
        list[dict]: Internship records joined with company name.
    """
    connection = get_db_connection()
    if connection is None:
        return []

    try:
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT i.*, c.Company_Name, c.Location, c.Industry_Type
            FROM Internships i
            JOIN Companies c ON i.Company_ID = c.Company_ID
            ORDER BY i.Application_Deadline
        """
        cursor.execute(query)
        return cursor.fetchall()

    except Error as err:
        print(f"[MODEL ERROR] get_all_internships: {err}")
        return []

    finally:
        cursor.close()
        connection.close()


def get_internships_by_company(company_id):
    """
    Retrieve all internships posted by a specific company.

    Args:
        company_id (int): The company's primary key.

    Returns:
        list[dict]: Internship records for that company.
    """
    connection = get_db_connection()
    if connection is None:
        return []

    try:
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT i.*, c.Company_Name
            FROM Internships i
            JOIN Companies c ON i.Company_ID = c.Company_ID
            WHERE i.Company_ID = %s
            ORDER BY i.Application_Deadline
        """
        cursor.execute(query, (company_id,))
        return cursor.fetchall()

    except Error as err:
        print(f"[MODEL ERROR] get_internships_by_company: {err}")
        return []

    finally:
        cursor.close()
        connection.close()


def get_recommended_internships(student_id):
    """
    Recommend internships where the student's skills match.

    Logic:
        1. Get the student's skill names from the Skills table.
        2. For each internship, check if any student skill appears
           in the Required_Skills column (simple substring match).
        3. Return matching internships sorted by match count.

    Args:
        student_id (int): The student's primary key.

    Returns:
        list[dict]: Matching internships with a 'match_count' field.
    """
    connection = get_db_connection()
    if connection is None:
        return []

    try:
        cursor = connection.cursor(dictionary=True)

        # Step 1 — get student's skills
        cursor.execute(
            "SELECT Skill_Name FROM Skills WHERE Student_ID = %s",
            (student_id,),
        )
        skills = [row["Skill_Name"].lower() for row in cursor.fetchall()]

        if not skills:
            return []

        # Step 2 — get all internships
        cursor.execute("""
            SELECT i.*, c.Company_Name, c.Location
            FROM Internships i
            JOIN Companies c ON i.Company_ID = c.Company_ID
            WHERE i.Application_Deadline >= CURDATE()
            ORDER BY i.Application_Deadline
        """)
        internships = cursor.fetchall()

        # Step 3 — match skills (simple case-insensitive substring match)
        recommendations = []
        for internship in internships:
            required = (internship.get("Required_Skills") or "").lower()
            match_count = sum(
                1 for skill in skills if skill in required
            )
            if match_count > 0:
                internship["match_count"] = match_count
                recommendations.append(internship)

        # Sort by number of matching skills (most matches first)
        recommendations.sort(key=lambda x: x["match_count"], reverse=True)
        return recommendations

    except Error as err:
        print(f"[MODEL ERROR] get_recommended_internships: {err}")
        return []

    finally:
        cursor.close()
        connection.close()
