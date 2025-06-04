from flask import Flask, render_template
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
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT DoctorFirstName, DoctorLastName, DoctorBio FROM Doctor")
    doctors = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('doctor-dashboard.html', doctors=doctors)

if __name__ == '__main__':
    app.run(debug=True)
