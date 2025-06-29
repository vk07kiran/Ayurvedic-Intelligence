from flask import Blueprint, render_template

yoga_bp = Blueprint('yoga', __name__, template_folder='../templates')

@yoga_bp.route('/yoga')
def yoga():
    return render_template('Yoga.html')
