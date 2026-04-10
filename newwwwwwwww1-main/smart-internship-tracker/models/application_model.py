"""
==============================================================
Smart Internship Tracker System — Application Model
==============================================================
Handles database operations for internship applications.
==============================================================
"""

from mysql.connector import Error
from database.db_connection import get_db_connection

# Valid status transitions (current -> allowed next statuses)
VALID_STATUSES = {"Applied", "Interview Scheduled", "Selected", "Rejected"}


def create_application(student_id, internship_id, application_date):
    """
    Record a student's application for an internship.

    Args:
        student_id (int): FK to Students.
        internship_id (int): FK to Internships.
        application_date (str): Date string "YYYY-MM-DD".

    Returns:
        dict: Success status and new application ID, or error.
    """
    connection = get_db_connection()
    if connection is None:
        return {"success": False, "error": "Database connection failed"}

    try:
        cursor = connection.cursor()
        query = """
            INSERT INTO Applications
                (Student_ID, Internship_ID, Application_Date, Application_Status)
            VALUES (%s, %s, %s, 'Applied')
        """
        cursor.execute(query, (student_id, internship_id, application_date))
        connection.commit()

        return {"success": True, "application_id": cursor.lastrowid}

    except Error as err:
        # MySQL error 1062 = Duplicate entry (student already applied)
        if err.errno == 1062:
            return {
                "success": False,
                "error": "Student has already applied for this internship",
            }
        return {"success": False, "error": str(err)}

    finally:
        cursor.close()
        connection.close()


def get_student_applications(student_id):
    """
    Get all applications submitted by a specific student.

    Args:
        student_id (int): The student's primary key.

    Returns:
        list[dict]: Application records with internship and company info.
    """
    connection = get_db_connection()
    if connection is None:
        return []

    try:
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT
                a.Application_ID,
                a.Application_Date,
                a.Application_Status,
                i.Role,
                i.Duration,
                i.Stipend,
                c.Company_Name,
                c.Location
            FROM Applications a
            JOIN Internships i ON a.Internship_ID = i.Internship_ID
            JOIN Companies   c ON i.Company_ID   = c.Company_ID
            WHERE a.Student_ID = %s
            ORDER BY a.Application_Date DESC
        """
        cursor.execute(query, (student_id,))
        return cursor.fetchall()

    except Error as err:
        print(f"[MODEL ERROR] get_student_applications: {err}")
        return []

    finally:
        cursor.close()
        connection.close()


def update_application_status(application_id, new_status):
    """
    Update the status of an existing application.

    Args:
        application_id (int): PK of the application.
        new_status (str): One of the VALID_STATUSES values.

    Returns:
        dict: Success or error information.
    """
    if new_status not in VALID_STATUSES:
        return {
            "success": False,
            "error": f"Invalid status. Must be one of: {VALID_STATUSES}",
        }

    connection = get_db_connection()
    if connection is None:
        return {"success": False, "error": "Database connection failed"}

    try:
        cursor = connection.cursor()
        query = """
            UPDATE Applications
            SET Application_Status = %s
            WHERE Application_ID = %s
        """
        cursor.execute(query, (new_status, application_id))
        connection.commit()

        if cursor.rowcount == 0:
            return {"success": False, "error": "Application not found"}

        return {"success": True, "message": "Status updated successfully"}

    except Error as err:
        return {"success": False, "error": str(err)}

    finally:
        cursor.close()
        connection.close()


def get_all_applications():
    """
    Retrieve every application (used by Placement Cell dashboard).

    Returns:
        list[dict]: All application records with student, internship,
                    and company details.
    """
    connection = get_db_connection()
    if connection is None:
        return []

    try:
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT
                a.Application_ID,
                s.Name        AS Student_Name,
                s.Department,
                c.Company_Name,
                i.Role,
                a.Application_Date,
                a.Application_Status
            FROM Applications a
            JOIN Students    s ON a.Student_ID    = s.Student_ID
            JOIN Internships i ON a.Internship_ID = i.Internship_ID
            JOIN Companies   c ON i.Company_ID    = c.Company_ID
            ORDER BY a.Application_Date DESC
        """
        cursor.execute(query)
        return cursor.fetchall()

    except Error as err:
        print(f"[MODEL ERROR] get_all_applications: {err}")
        return []

    finally:
        cursor.close()
        connection.close()


def get_application_statistics():
    """
    Get a count of applications grouped by status.
    Useful for the placement cell dashboard.

    Returns:
        list[dict]: e.g. [{"status": "Applied", "count": 5}, ...]
    """
    connection = get_db_connection()
    if connection is None:
        return []

    try:
        cursor = connection.cursor(dictionary=True)
        query = """
            SELECT
                Application_Status AS status,
                COUNT(*)           AS count
            FROM Applications
            GROUP BY Application_Status
        """
        cursor.execute(query)
        return cursor.fetchall()

    except Error as err:
        print(f"[MODEL ERROR] get_application_statistics: {err}")
        return []

    finally:
        cursor.close()
        connection.close()
