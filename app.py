from flask import Flask, redirect, url_for
from blueprints.dashboard import dashboard_bp
from blueprints.profile import profile_bp
from blueprints.login import login_bp
from blueprints.signup import signup_bp
from blueprints.LandingPage import landing_bp
from blueprints.ChatbotMain import chatbotmain_bp

import os

app = Flask(
    __name__,
    template_folder='templates',
    static_folder='static/assets'
)

# Configuration
app.config['UPLOAD_FOLDER'] = os.path.abspath(os.path.join(os.path.dirname(__file__), 'Images'))
app.config['ALLOWED_EXTENSIONS'] = {'jpg', 'jpeg', 'png'}
app.config['DB_CONFIG'] = {
    'host': 'localhost',
    'user': 'root',
    'password': '',
    'database': 'userdb'
}

# Generate a strong random secret key
app.secret_key = os.urandom(24)

# Register Blueprints
app.register_blueprint(login_bp)
app.register_blueprint(signup_bp)
app.register_blueprint(dashboard_bp)
app.register_blueprint(profile_bp)
app.register_blueprint(landing_bp)
app.register_blueprint(chatbotmain_bp)

# Default route: Redirect to login
@app.route('/')
def index():
    return redirect(url_for('login.login'))  # login = blueprint name

# Start the Flask app
if __name__ == '__main__':
    app.run(debug=True)
