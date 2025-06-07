from flask import Flask, request, render_template, redirect, url_for
import mysql.connector
import bcrypt

app = Flask(__name__, template_folder='../templates', static_folder='../static')

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'userdb'
}

@app.route('/')
def index():
    return render_template('LoginSignup.html')  # Your updated HTML

@app.route('/signup', methods=['POST'])
def signup():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    
    # Debugging: Print received data
    print(f"Received data: username={username}, email={email}, password={password}")
    
    # Hash the password
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    
    try:
        # Connect to the database
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        
        # Prepare SQL query
        query = "INSERT INTO users (username, email, password) VALUES (%s, %s, %s)"
        
        # Execute the query
        cursor.execute(query, (username, email, hashed_password))
        
        # Commit the changes
        conn.commit()

        # Debugging: Check if row was inserted
        print(f"Inserted {cursor.rowcount} row(s) into the database.")
        
    except mysql.connector.Error as err:
        # Handle database errors
        print(f"Error: {err}")
        return f"Error occurred: {err}"
    
    finally:
        # Close cursor and connection
        cursor.close()
        conn.close()

    return redirect(url_for('index'))  # Redirect to the login page


# Login Route
@app.route('/login', methods=['POST'])
def login():
    username = request.form['loginusername']
    password = request.form['loginpassword']

    # Connect to MySQL database
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()

    # Retrieve stored hashed password for the user
    query = "SELECT password FROM users WHERE username = %s"
    cursor.execute(query, (username,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    if result and bcrypt.checkpw(password.encode('utf-8'), result[0].encode('utf-8')):
        # Successful login, redirect to the landing page or dashboard
        return redirect(url_for('landing_page'))
    else:
        # Invalid credentials, stay on the login page
        return "Invalid username or password. <a href='/'>Try again</a>"

@app.route('/landing')
def landing_page():
    return render_template('LandingPage.html')


if __name__ == '__main__':
    app.run(debug=True)
