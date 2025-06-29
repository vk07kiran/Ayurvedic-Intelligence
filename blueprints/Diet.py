from flask import Blueprint, render_template

diet_bp = Blueprint('diet', __name__, template_folder='../templates')

@diet_bp.route('/diet')
def diet():
    return render_template('Diet.html')
