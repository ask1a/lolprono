from flask import Blueprint
from . import db

auth = Blueprint('auth', __name__)

@auth.route('/login')
def index():
    return 'Login'

@auth.route('/signup')
def index():
    return 'Signup'

@auth.route('/logout')
def index():
    return 'Logout'