from flask import Blueprint, render_template, redirect, url_for, request
from flask_login import login_required, current_user
from . import db
from .models import UserLeague, Game
import pandas as pd
import io
from datetime import datetime, timedelta

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


@main.route('/admin')
def admin():
    return render_template('admin.html')


@main.route('/admin_add_games', methods=['POST'])
def admin_add_games():
    if 'gamesdata' not in request.files:
        return redirect(url_for('main.admin'))
    file = request.files['gamesdata']
    if file.filename == '':
        return redirect(url_for('main.admin'))
    if file.filename[-3:] != 'csv':
        return redirect(url_for('main.admin'))

    file_stream = io.BytesIO(file.read())
    games_to_load_in_database = pd.read_csv(file_stream).to_dict("records")

    for game in games_to_load_in_database:
        # check if game already exist then delete to overwrite:
        check_exist = {}
        row = Game.query.filter(
            Game.gamedatetime <= datetime.fromisoformat(game['gamedatetime']) + timedelta(minutes=1),
            Game.gamedatetime >= datetime.fromisoformat(game['gamedatetime']) - timedelta(minutes=1),
            Game.team1 == game['team1'],
            Game.team2 == game['team2']
        ).first()
        if row:
            check_exist['gameid'] = row.id
            print("suppression enregistrement")
            # delete the game in database
            db.session.delete(row)
            db.session.commit()

        # create a game with the csv data.
        new_game = Game(
            leagueid=game['leagueid'],
            bo=game['bo'],
            gamedatetime=datetime.fromisoformat(game['gamedatetime']),
            team1=game['team1'],
            team2=game['team2'],
            team1score=game['team1score'],
            team2score=game['team2score']
        )
        if check_exist.get('gameid'):
            new_game.id = check_exist.get('gameid')
        # add the new user to the database
        db.session.add(new_game)
        db.session.commit()

    return render_template('admin.html')
