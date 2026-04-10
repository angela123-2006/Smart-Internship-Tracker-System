"""
==============================================================
Smart Internship Tracker System — Notification Model
==============================================================
Handles database operations for student notifications.
==============================================================
"""

from mysql.connector import Error
from database.db_connection import get_db_connection


def create_notification(student_id, message):
    """
    Create a notification for a student.

    Args:
        student_id (int): FK to Students.
        message (str): Notification text.

    Returns:
        dict: Success status and notification ID, or error.
    """
    connection = get_db_connection()
    if connection is None:
        return {"success": False, "error": "Database connection failed"}

    try:
        cursor = connection.cursor()
        query = """
            INSERT INTO Notifications (Student_ID, Message)
            VALUES (%s, %s)
        """
        cursor.execute(query, (student_id, message))
        connection.commit()

        return {"success": True, "notification_id": cursor.lastrowid}

    except Error as err:
        return {"success": False, "error": str(err)}

    finally:
        cursor.close()
        connection.close()


def get_student_notifications(student_id):
    """
    Retrieve all notifications for a student, newest first.

    Args:
        student_id (int): The student's primary key.

    Returns:
        list[dict]: Notification records for that student.
    """
    connection = get_db_connection()
    if connection is None:
        return []

    try:
        cursor = connection.cursor(dictionary=True)
        cursor.execute(
            """SELECT * FROM Notifications
               WHERE Student_ID = %s
               ORDER BY Notification_Date DESC""",
            (student_id,),
        )
        return cursor.fetchall()

    except Error as err:
        print(f"[MODEL ERROR] get_student_notifications: {err}")
        return []

    finally:
        cursor.close()
        connection.close()
