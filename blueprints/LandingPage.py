from flask import Blueprint, render_template, session, redirect, url_for
import mysql.connector

landing_bp = Blueprint('landing', __name__)

def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='userdb'
    )

@landing_bp.route('/landing')
def landing_page():
    # Get user ID from session
    patient_user_id = session.get('user_id')

    if not patient_user_id:
        return redirect(url_for('login.login'))  # Not logged in, redirect to login

    # Connect to DB and fetch patient details
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM patient WHERE PatientUserId = %s", (patient_user_id,))
    patient_data = cursor.fetchone()
    cursor.close()
    conn.close()

    if not patient_data:
        return "Patient not found", 404

    # Render the landing page with patient data
    return render_template('LandingPage.html', patient=patient_data)

@landing_bp.route('/logout')
def logout():
    session.clear()  # Clears all session data (user_id, username, etc.)
    return redirect(url_for('login.login'))  # Redirect to login page