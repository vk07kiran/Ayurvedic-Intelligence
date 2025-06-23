from flask import Blueprint, render_template, request, send_from_directory
from flask import Blueprint, render_template, request, redirect, url_for, send_from_directory

import mysql.connector
import os

dashboard_bp = Blueprint('dashboard', __name__)

def get_db_connection():
    return mysql.connector.connect(
        host='localhost', user='root', password='', database='userdb'
    )

IMAGE_UPLOAD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '../Images'))

@dashboard_bp.route('/Images/<filename>')
def uploaded_image(filename):
    return send_from_directory(IMAGE_UPLOAD_FOLDER, filename)

@dashboard_bp.route('/dashboard')
@dashboard_bp.route('/dashboard')
def show_Patient():
    Patient_id = request.args.get('id', '').strip()
    if not Patient_id:
        return redirect(url_for('login.login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM Patient WHERE PatientUserId = %s", (Patient_id,))
    patient = cursor.fetchone()

    if not patient:
        cursor.close()
        conn.close()
        return f"<h3 style='color:red;'>No Patient found with ID: {Patient_id}</h3>", 404

    cursor.close()
    conn.close()
    return render_template('Patient-dashboard.html', patient=patient)
