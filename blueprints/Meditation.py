from flask import Blueprint, render_template

meditation_bp = Blueprint('meditation', __name__, template_folder='../templates')

@meditation_bp.route('/meditation')
def meditation():
    return render_template('Meditation.html')
