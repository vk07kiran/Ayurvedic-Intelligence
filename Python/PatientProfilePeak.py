from flask import Flask, request, render_template
import mysql.connector

app = Flask(__name__, template_folder='../templates', static_folder='../static/assets')

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'userdb'
}

@app.route('/')
def index():
    user_id = request.args.get('id')

    if not user_id:
        return "UserID is required in the URL. Example: /?id=U004", 400

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        query = '''
        SELECT
            p.PatientProfilePic,
            p.PatientFirstName AS PatientFirstName,
            p.PatientLastName AS PatientLastName,
            u.UserID,
            p.PatientAddress,
            p.PatientMobile,
            p.PatientBloodGroup,
            p.PatientAppointedDoctorID,
            d.DoctorFirstName,
            d.DoctorLastName,
            p.PatientPrescriptionName,
            p.PatientDOB,
            p.PatientRecords,
            p.PatientPrescriptionDate,
            PatientPrescriptionDoctorName,
            p.PatientBillingAmount,
            p.PatientBillingDate,
            p.PatientBillingInvoiceNo,
            p.PatientAppointmentDate,
            d.DoctorProfilePic,
            d.DoctorSpecialization
        FROM
            Patient p
        JOIN
            Users u ON p.PatientUserId = u.UserID
        LEFT JOIN
            Doctor d ON p.PatientAppointedDoctorID = d.DoctorID
        WHERE
            u.UserID = %s
        '''

        cursor.execute(query, (user_id,))
        patient_data = cursor.fetchone()

        if not patient_data:
            return f"No data found for UserID: {user_id}", 404

        # Construct current URL
        full_url = request.base_url + "?id=" + user_id

        return render_template('patient-profile.html', data=patient_data, url=full_url)

    except mysql.connector.Error as err:
        return f"Database error: {err}", 500

    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()
if __name__ == '__main__':
    app.run(debug=True)


