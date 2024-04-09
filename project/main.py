from flask import Blueprint, render_template
from flask_login import login_required, current_user
from . import db

main = Blueprint('main', __name__)


@main.route('/index')
def index():
    return render_template('index.html')


@main.route('/profile')
@login_required
def profile():
    # return "Salut {name}, ton email est : {email}, ton id est : {id}".format(name = current_user.name, email = current_user.email, id = current_user.id)
    return render_template('profile.html', name=current_user.name)
