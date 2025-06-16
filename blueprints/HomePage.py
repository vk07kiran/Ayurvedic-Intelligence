from flask import Blueprint, render_template, request, send_from_directory
import mysql.connector
import os

homepage_bp = Blueprint('homepage', __name__)


def get_db_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='userdb'
    )

@homepage_bp.route('/homepage')
def landing_page():
    return render_template('HomePage.html')

