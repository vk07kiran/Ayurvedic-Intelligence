from flask import Blueprint, render_template, request, redirect, url_for, send_from_directory
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
    doctor_id = request.args.get('id', '').strip()
    if not doctor_id:
        return "<h3 style='color:red;'>Doctor ID not provided in URL.</h3>", 400

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Doctor WHERE DoctorID = %s", (doctor_id,))
    doctor = cursor.fetchone()
    cursor.execute("SELECT * FROM Users WHERE UserID = %s", (doctor_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    return render_template('doctor-profile-settings.html', doctor=doctor, user=user)

@profile_bp.route('/submit', methods=['POST'])
def submit_doctor():
    data = request.form.to_dict()
    doctor_id = data.get('DoctorID') or str(uuid.uuid4())

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT DoctorProfilePic FROM Doctor WHERE DoctorID = %s", (doctor_id,))
    row = cursor.fetchone()
    existing_profile_pic = row[0] if row else ""

    profile_pic = request.files.get("DoctorProfilePic")
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

    data['DoctorProfilePic'] = profile_pic_filename

    uploaded_images = request.files.getlist("DoctorImages")
    saved_image_filenames = []
    for file in uploaded_images:
        if file and allowed_file(file.filename):
            ext = file.filename.rsplit('.', 1)[1].lower()
            timestamp = int(time.time() * 1000)
            filename = f"image_{timestamp}.{ext}"
            secure_name = secure_filename(filename)
            file.save(os.path.join(IMAGE_UPLOAD_FOLDER, secure_name))
            saved_image_filenames.append(secure_name)

    data['DoctorImages'] = ','.join(saved_image_filenames)

    cursor.execute("SELECT DoctorID FROM Doctor WHERE DoctorID = %s", (doctor_id,))
    exists = cursor.fetchone()

    try:
        if exists:
            # Placeholder for update query
            # Update existing record
            query = """
            UPDATE Doctor SET
                DoctorProfilePic=%s, DoctorFirstName=%s, DoctorLastName=%s,
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
                data.get('DoctorProfilePic'),
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
            pass
        else:
            # Placeholder for insert query
            # Insert new doctor record
            query = """
            INSERT INTO Doctor (
                DoctorProfilePic, DoctorID, DoctorFirstName, DoctorLastName,
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
                data.get('DoctorProfilePic'), doctor_id,
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
        pass
        
    except Exception as e:
        print("Database Error:", e)
    finally:
        cursor.close()
        conn.close()

    return redirect(url_for('profile.edit_profile', id=doctor_id))
