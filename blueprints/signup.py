from flask import Blueprint, render_template, request, redirect, url_for, flash
import mysql.connector
import uuid

signup_bp = Blueprint('signup', __name__, template_folder='../templates')

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'userdb'
}

def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

@signup_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']  # plain password for now
        role = "Patient"
        user_id = str(uuid.uuid4())

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check for existing email
        cursor.execute("SELECT * FROM Users WHERE UserEmail = %s", (email,))
        if cursor.fetchone():
            flash('Email already registered.')
            cursor.close()
            conn.close()
            return redirect(url_for('signup.signup'))

        # Insert into Users
        cursor.execute(
            "INSERT INTO Users (UserID, Username, UserEmail, UserPassword, UserType) VALUES (%s, %s, %s, %s, %s)",
            (user_id, username, email, password, role)
        )

        # Insert into Patient or Patient table based on role
        if role == 'Patient':
            cursor.execute(
                "INSERT INTO Patient (PatientUserId, PatientProfilePic) VALUES (%s, 'img')",
                (user_id,)
            )
        elif role == 'patient':
            cursor.execute(
                "INSERT INTO Patient (PatientUserId, PatientProfilePic) VALUES (%s, 'img')",
                (user_id,)
            )

        conn.commit()
        cursor.close()
        conn.close()

        flash('Account created successfully. Please log in.')
        return redirect(url_for('login.login'))

    return render_template('register.html')