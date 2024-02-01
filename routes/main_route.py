# Imports:
from flask import Blueprint, render_template

# Blueprint constructor:
main_bp = Blueprint('main_bp', __name__)

# Home route:
@main_bp.route('/')
def home():
    return render_template('index.html')

# Error route:
@main_bp.route('/error')
def error():
    return render_template('error.html')
