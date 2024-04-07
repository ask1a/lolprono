from flask import Blueprint
from . import db

main = Blueprint('auth', __name__)

@main.route('/login')
def index():
    return 'Login'

@main.route('/signup')
def index():
    return 'Signup'

@main.route('/logout')
def index():
    return 'Logout'