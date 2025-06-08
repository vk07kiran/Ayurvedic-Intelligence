from flask import Blueprint, render_template, request, send_from_directory
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
def show_doctor():
    doctor_id = request.args.get('id', '').strip()
    if not doctor_id:
        return "<h3 style='color:red;'>Doctor ID not provided in URL.</h3>", 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM Doctor WHERE DoctorID = %s", (doctor_id,))
    doctor = cursor.fetchone()

    if not doctor:
        cursor.close()
        conn.close()
        return f"<h3 style='color:red;'>No doctor found with ID: {doctor_id}</h3>", 404

    appointed_user_id = doctor.get('AppointedByUser')
    patient = None
    if appointed_user_id:
        cursor.execute("SELECT * FROM Patient WHERE PatientUserId = %s", (appointed_user_id,))
        patient = cursor.fetchone()

    cursor.close()
    conn.close()
    return render_template('doctor-dashboard.html', doctor=doctor, patient=patient)
