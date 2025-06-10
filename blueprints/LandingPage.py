from flask import Blueprint, render_template, request, send_from_directory
import mysql.connector
import os

landing_bp = Blueprint('landing', __name__)


def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='userdb'
    )

@landing_bp.route('/landing')
def landing_page():
    return render_template('LandingPage.html')
