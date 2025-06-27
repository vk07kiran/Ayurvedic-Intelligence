from flask import Blueprint, render_template, request, redirect, url_for, send_from_directory, session
import mysql.connector
import os, time, uuid
from werkzeug.utils import secure_filename

profile_bp = Blueprint('profile', __name__)

IMAGE_UPLOAD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '../Images'))

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'jpg', 'jpeg', 'png'}

def get_db_connection():
    return mysql.connector.connect(
        host='localhost', user='root', password='', database='userdb'
    )

@profile_bp.route('/editprofile')
def edit_profile():
    Patient_id = session.get('user_id')
    if not Patient_id:
        return redirect(url_for('login.login'))

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Patient WHERE PatientUserId = %s", (Patient_id,))
    patient = cursor.fetchone()
    cursor.execute("SELECT * FROM Users WHERE UserID = %s", (Patient_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    return render_template('Patient-profile-settings.html', patient=patient, user=user)

@profile_bp.route('/submit', methods=['POST'])
def submit_Patient():
    data = request.form.to_dict()
    Patient_id = data.get('PatientUserId') or str(uuid.uuid4())

    conn = get_db_connection()
    cursor = conn.cursor()

    # Get existing profile pic if present
    cursor.execute("SELECT PatientProfilePic FROM Patient WHERE PatientUserId = %s", (Patient_id,))
    row = cursor.fetchone()
    existing_profile_pic = row[0] if row else ""

    profile_pic = request.files.get("PatientProfilePic")
    profile_pic_filename = existing_profile_pic

    if profile_pic and allowed_file(profile_pic.filename):
        ext = profile_pic.filename.rsplit('.', 1)[1].lower()
        timestamp = int(time.time() * 1000)
        new_filename = f"profile_pic_{timestamp}.{ext}"
        secure_name = secure_filename(new_filename)
        if not os.path.exists(IMAGE_UPLOAD_FOLDER):
            os.makedirs(IMAGE_UPLOAD_FOLDER)
        profile_pic.save(os.path.join(IMAGE_UPLOAD_FOLDER, secure_name))
        profile_pic_filename = secure_name

    data['PatientProfilePic'] = profile_pic_filename

    # Check if record already exists
    cursor.execute("SELECT PatientUserId FROM Patient WHERE PatientUserId = %s", (Patient_id,))
    exists = cursor.fetchone()

    try:
        if exists:
            # Update existing patient record
            query = """
            UPDATE Patient SET
                PatientProfilePic=%s, PatientFirstName=%s, PatientLastName=%s, PatientDOB=%s,
                PatientBloodGroup=%s, PatientMobile=%s, PatientAddress=%s, PatientCity=%s,
                PatientState=%s, PatientZipCode=%s, PatientCountry=%s
            WHERE PatientUserId = %s
            """
            values = (
                data.get('PatientProfilePic'), data.get('PatientFirstName'), data.get('PatientLastName'),
                data.get('PatientDOB'), data.get('PatientBloodGroup'), data.get('PatientMobile'),
                data.get('PatientAddress'), data.get('PatientCity'), data.get('PatientState'),
                data.get('PatientZipCode'), data.get('PatientCountry'), Patient_id
            )
        else:
            # Insert new patient record
            query = """
            INSERT INTO Patient (
                PatientUserId, PatientProfilePic, PatientFirstName, PatientLastName, PatientDOB,
                PatientBloodGroup, PatientMobile, PatientAddress, PatientCity, PatientState,
                PatientZipCode, PatientCountry
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (
                Patient_id, data.get('PatientProfilePic'), data.get('patientFirstName'), data.get('PatientLastName'),
                data.get('PatientDOB'), data.get('PatientBloodGroup'), data.get('PatientMobile'),
                data.get('PatientAddress'), data.get('PatientCity'), data.get('PatientState'),
                data.get('PatientZipCode'), data.get('PatientCountry')
            )

        cursor.execute(query, values)
        conn.commit()

    except Exception as e:
        print("Database Error:", e)
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('profile.edit_profile', id=Patient_id))


@profile_bp.route('/logout')
def logout():
    session.clear()  # Clears all session data (user_id, username, etc.)
    return redirect(url_for('login.login'))  # Redirect to login page