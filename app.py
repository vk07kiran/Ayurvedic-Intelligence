from flask import Flask
from blueprints.dashboard import dashboard_bp
from blueprints.profile import profile_bp
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

# Register Blueprints
app.register_blueprint(dashboard_bp)
app.register_blueprint(profile_bp)

# Start the Flask app
if __name__ == '__main__':
    app.run(debug=True)
