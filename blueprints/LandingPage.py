from flask import Blueprint, render_template, request
from flask import Blueprint, render_template, request, redirect, url_for, send_from_directory

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
    patient_user_id = request.args.get('id')  # get the PatientUserId from URL query param

    if not patient_user_id:
        return redirect(url_for('login.login'))

    # connect to DB and fetch patient details
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM patient WHERE PatientUserId = %s", (patient_user_id,))
    patient_data = cursor.fetchone()
    cursor.close()
    conn.close()

    if not patient_data:
        return "Patient not found", 404

    # render the landing page with patient data
    return render_template('LandingPage.html', patient=patient_data)
