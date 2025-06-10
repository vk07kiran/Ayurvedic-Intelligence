from flask import Blueprint, render_template, request, redirect, url_for, flash, session
import mysql.connector
from werkzeug.security import check_password_hash

login_bp = Blueprint('login', __name__, template_folder='../templates')

# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'userdb'
}

# Create DB connection
def get_db_connection():
    return mysql.connector.connect(**DB_CONFIG)

# Login route
@login_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash('Email and password are required.', 'error')
            return redirect(url_for('login.login'))

        conn = get_db_connection()
        cursor = conn.cursor(dictionary=True)

        # Check if user exists
        cursor.execute("SELECT * FROM Users WHERE UserEmail = %s", (email,))
        user = cursor.fetchone()

        # if user and check_password_hash(user['UserPassword'], password):
        if user and user['UserPassword'] == password:
            # Store user session
            session['user_id'] = user['UserID']
            session['username'] = user['Username']

            # Check if the user is a doctor
            cursor.execute("SELECT * FROM Users WHERE UserID = %s AND UserType= 'Doctor' ", (user['UserID'],))
            doctor = cursor.fetchone()
            patient = cursor.fetchone()

            cursor.close()
            conn.close()

            if doctor:
                # Redirect to doctor dashboard
                return redirect(url_for('dashboard.show_doctor', id=doctor['UserID']))
            
            else:
                return redirect(url_for('landing.landing_page'))
                
        else:
            cursor.close()
            conn.close()
            flash('Invalid email or password.', 'error')
            return redirect(url_for('login.login'))

    return render_template('login.html')

# Logout route
@login_bp.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login.login'))
