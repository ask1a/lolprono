from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user
from . import db
from .models import UserLeague

main = Blueprint('main', __name__)


@main.route('/index')
def index():
    return render_template('index.html')


@main.route('/profile')
@login_required
def profile():
    current_user_league_list = [e.leaguename for e in
                                UserLeague.query.filter_by(userid=current_user.id).order_by(UserLeague.leagueid).all()]
    return render_template('profile.html', name=current_user.name, league_list=current_user_league_list)


@main.route('/profile_unsubscribe_league/<leaguename>', methods=['POST'])
@login_required
def profile_unsubscribe_league_post(leaguename):
    row = UserLeague.query.filter_by(userid=current_user.id, leaguename=leaguename).first()

    # delete the userleague to the database
    db.session.delete(row)
    db.session.commit()

    return redirect(url_for('main.profile'))


