from flask import Flask, request, render_template, redirect, url_for
import mysql.connector
import uuid
import os
from werkzeug.utils import secure_filename
from flask import send_from_directory
import time


app = Flask(__name__, template_folder='../templates', static_folder='../static/assets')

# Configuration
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'userdb'
}

ALLOWED_EXTENSIONS = {'jpg', 'jpeg','png'}
IMAGE_UPLOAD_FOLDER = os.path.abspath(os.path.join(os.path.dirname(__file__), '../Images'))


# Helper: Check if file is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Helper: DB Connection
def get_db_connection():
    return mysql.connector.connect(**db_config)

@app.route('/Images/<filename>')
def uploaded_image(filename):
    return send_from_directory(IMAGE_UPLOAD_FOLDER, filename)

# Route: Doctor Profile Form
@app.route('/', methods=['GET'])
def index():
    doctor_id = request.args.get('id')  # e.g. ?id=some-uuid
    doctor = {}

    if doctor_id:
        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Doctor WHERE DoctorID = %s", (doctor_id,))
        doctor = cursor.fetchone()
        cursor.close()
        conn.close()

    return render_template('doctor-profile-settings.html', doctor=doctor)

@app.route('/submit', methods=['POST'])
def submit_doctor():
    data = request.form.to_dict()
    doctor_id = data.get('DoctorID') or str(uuid.uuid4())

    # Connect to DB and fetch existing profile pic filename if doctor exists
    existing_profile_pic = ""
    conn = get_db_connection()
    cursor = conn.cursor()
    if doctor_id:
        cursor.execute("SELECT DoctorProfilePic FROM Doctor WHERE DoctorID = %s", (doctor_id,))
        row = cursor.fetchone()
        if row:
            existing_profile_pic = row[0]
    cursor.close()
    conn.close()

    # === Handle DoctorProfilePic Upload ===
    profile_pic = request.files.get("DoctorProfilePic")
    profile_pic_filename = existing_profile_pic  # default to existing

    if profile_pic and allowed_file(profile_pic.filename) and profile_pic.filename != '':
        ext = profile_pic.filename.rsplit('.', 1)[1].lower()
        timestamp = int(time.time() * 1000)  # current time in ms
        new_filename = f"profile_pic_{timestamp}.{ext}"
        secure_name = secure_filename(new_filename)

        if not os.path.exists(IMAGE_UPLOAD_FOLDER):
            os.makedirs(IMAGE_UPLOAD_FOLDER)

        save_path = os.path.join(IMAGE_UPLOAD_FOLDER, secure_name)
        profile_pic.save(save_path)
        profile_pic_filename = secure_name

    data['DoctorProfilePic'] = profile_pic_filename

    # === Handle DoctorImages Upload (multiple files) ===
    uploaded_images = request.files.getlist("DoctorImages")
    saved_image_filenames = []

    for file in uploaded_images:
        if file and allowed_file(file.filename):
            ext = file.filename.rsplit('.', 1)[1].lower()
            timestamp = int(time.time() * 1000)  # current time in milliseconds
            new_filename = f"image_{timestamp}.{ext}"
            secure_name = secure_filename(new_filename)
            file.save(os.path.join(IMAGE_UPLOAD_FOLDER, secure_name))
            saved_image_filenames.append(secure_name)

    data['DoctorImages'] = ','.join(saved_image_filenames)

    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if the doctor already exists
    cursor.execute("SELECT DoctorID FROM Doctor WHERE DoctorID = %s", (doctor_id,))
    exists = cursor.fetchone()

    try:
        if exists:
            # Update existing record
            query = """
            UPDATE Doctor SET
                DoctorProfilePic=%s, DoctorUsename=%s, DoctorEmail=%s, DoctorFirstName=%s, DoctorLastName=%s,
                DoctorPhone=%s, DoctorGender=%s, DoctorDOB=%s, DoctorBio=%s,
                DoctorClinicName=%s, DoctorClinicAddress=%s, DoctorImages=%s,
                DoctorAddress1=%s, DoctorAddress2=%s, DoctorCity=%s, DoctorState=%s,
                DoctorCountry=%s, DoctorPostalCode=%s, DoctorFeePerHour=%s, DoctorSpecialization=%s,
                DoctorServices=%s, DoctorDegreeName=%s, DoctorCollege=%s, DoctorYearOfCompletion=%s,
                DoctorExperienceHospital=%s, DoctorExperienceFromYear=%s, DoctorExperienceToYear=%s,
                DoctorExperienceDesignation=%s, DoctorAward=%s, DoctorAwardYear=%s,
                DoctorMemberships=%s, DoctorRegistrations=%s, DoctorRegistrationYear=%s
            WHERE DoctorID = %s
            """
            values = (
                data.get('DoctorProfilePic'), data.get('DoctorUsename'), data.get('DoctorEmail'),
                data.get('DoctorFirstName'), data.get('DoctorLastName'), data.get('DoctorPhone'),
                data.get('DoctorGender'), data.get('DoctorDOB'), data.get('DoctorBio'),
                data.get('DoctorClinicName'), data.get('DoctorClinicAddress'), data.get('DoctorImages'),
                data.get('DoctorAddress1'), data.get('DoctorAddress2'), data.get('DoctorCity'),
                data.get('DoctorState'), data.get('DoctorCountry'), data.get('DoctorPostalCode'),
                data.get('DoctorFeePerHour'), data.get('DoctorSpecialization'), data.get('DoctorServices'),
                data.get('DoctorDegreeName'), data.get('DoctorCollege'), data.get('DoctorYearOfCompletion'),
                data.get('DoctorExperienceHospital'), data.get('DoctorExperienceFromYear'),
                data.get('DoctorExperienceToYear'), data.get('DoctorExperienceDesignation'),
                data.get('DoctorAward'), data.get('DoctorAwardYear'), data.get('DoctorMemberships'),
                data.get('DoctorRegistrations'), data.get('DoctorRegistrationYear'), doctor_id
            )
        else:
            # Insert new doctor record
            query = """
            INSERT INTO Doctor (
                DoctorProfilePic, DoctorID, DoctorUsename, DoctorEmail, DoctorFirstName, DoctorLastName,
                DoctorPhone, DoctorGender, DoctorDOB, DoctorBio, DoctorClinicName,
                DoctorClinicAddress, DoctorImages, DoctorAddress1, DoctorAddress2, DoctorCity,
                DoctorState, DoctorCountry, DoctorPostalCode, DoctorFeePerHour, DoctorSpecialization,
                DoctorServices, DoctorDegreeName, DoctorCollege, DoctorYearOfCompletion,
                DoctorExperienceHospital, DoctorExperienceFromYear, DoctorExperienceToYear,
                DoctorExperienceDesignation, DoctorAward, DoctorAwardYear, DoctorMemberships,
                DoctorRegistrations, DoctorRegistrationYear
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                      %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            values = (
                data.get('DoctorProfilePic'), doctor_id, data.get('DoctorUsename'), data.get('DoctorEmail'),
                data.get('DoctorFirstName'), data.get('DoctorLastName'), data.get('DoctorPhone'),
                data.get('DoctorGender'), data.get('DoctorDOB'), data.get('DoctorBio'),
                data.get('DoctorClinicName'), data.get('DoctorClinicAddress'), data.get('DoctorImages'),
                data.get('DoctorAddress1'), data.get('DoctorAddress2'), data.get('DoctorCity'),
                data.get('DoctorState'), data.get('DoctorCountry'), data.get('DoctorPostalCode'),
                data.get('DoctorFeePerHour'), data.get('DoctorSpecialization'), data.get('DoctorServices'),
                data.get('DoctorDegreeName'), data.get('DoctorCollege'), data.get('DoctorYearOfCompletion'),
                data.get('DoctorExperienceHospital'), data.get('DoctorExperienceFromYear'),
                data.get('DoctorExperienceToYear'), data.get('DoctorExperienceDesignation'),
                data.get('DoctorAward'), data.get('DoctorAwardYear'), data.get('DoctorMemberships'),
                data.get('DoctorRegistrations'), data.get('DoctorRegistrationYear')
            )

        cursor.execute(query, values)
        conn.commit()

    except Exception as e:
        print("Database Error:", e)
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('index', id=doctor_id))


# @app.route('/dashboard')
# def dashboard():
#      return render_template('doctor-dashboard.html')

# Start Flask app
if __name__ == '__main__':
    app.run(debug=True)
    
