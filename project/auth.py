from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User, UserLeague, Game, GameProno, League
from flask_login import login_user, logout_user, login_required, current_user
from . import db
from sqlalchemy import select
import pandas as pd
import numpy as np
import io
from datetime import datetime, timedelta
from .utils import create_standing_table

auth = Blueprint('auth', __name__)
allowed_admin_account = ['skiaa@hotmail.com', 'zayedlewis@hotmail.com']


@auth.route('/login')
def login():
    return render_template('login.html')


@auth.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')
    remember = True if request.form.get('remember') else False

    user = User.query.filter_by(email=email).first()

    # check if the user actually exists
    # take the user-supplied password, hash it, and compare it to the hashed password in the database
    if not user or not check_password_hash(user.password, password):
        flash('Mauvais identifiants, email et/ou mot de passe incorrects.')
        return redirect(url_for('auth.login'))  # if the user doesn't exist or password is wrong, reload the page

    # if the above check passes, then we know the user has the right credentials
    login_user(user, remember=remember)
    return redirect(url_for('main.profile'))


@auth.route('/signup')
def signup():
    return render_template('signup.html')


@auth.route('/signup', methods=['POST'])
def signup_post():
    email = request.form.get('email')
    name = request.form.get('name')
    password = request.form.get('password')
    user = User.query.filter_by(
        email=email).first()  # if this returns a user, then the email already exists in database

    if user:  # if a user is found, we want to redirect back to signup page so user can try again
        flash("L'email existe déjà en base de donnée!")
        return redirect(url_for('auth.signup'))

    # create a new user with the form data. Hash the password so the plaintext version isn't saved.
    new_user = User(email=email, name=name, password=generate_password_hash(password, method='scrypt'))

    # add the new user to the database
    db.session.add(new_user)
    db.session.commit()

    # code to validate and add user to database goes here
    return redirect(url_for('auth.login'))


@auth.route('/ligues')
@login_required
def ligues():
    return render_template('ligues.html', league1=is_registered_in_league(1), league2=is_registered_in_league(2))


def add_userleague_row(leagueid, leaguename, userid):
    """Add new row in userleague table"""
    userleague = UserLeague.query.filter_by(userid=userid, leagueid=leagueid).first()
    if userleague:  # if a user/league already exist, dont go further.
        flash("Déjà inscrit à cette ligue!")
        return redirect(url_for('main.profile'))
    # create a new userleague's row with the form data.
    new_userleague = UserLeague(userid=userid, leagueid=leagueid, leaguename=leaguename)
    # add the new userleague to the database
    db.session.add(new_userleague)
    db.session.commit()
    return redirect(url_for('auth.pronos'))


def is_registered_in_league(leagueid):
    userleague = UserLeague.query.filter_by(userid=current_user.id, leagueid=leagueid).first()
    if userleague:
        return 1
    else:
        return 0


@auth.route('/ligue_spring', methods=['POST'])
@login_required
def ligue_spring_post():
    userid = current_user.id
    leagueid = 1
    leaguename = "LEC spring 2024"

    return add_userleague_row(leagueid, leaguename, userid)


@auth.route('/ligue_summer', methods=['POST'])
@login_required
def ligue_summer_post():
    userid = current_user.id
    leagueid = 2
    leaguename = "LEC summer 2024"

    return add_userleague_row(leagueid, leaguename, userid)


def get_current_user_league_list():
    current_user_league_list = [e.leaguename for e in
                                UserLeague.query.filter_by(userid=current_user.id).order_by(UserLeague.leagueid).all()]
    return current_user_league_list


def get_leagueid_from_leaguename(leaguename):
    row = UserLeague.query.filter_by(userid=current_user.id, leaguename=leaguename).first()
    leagueid = row.leagueid
    return leagueid


@auth.route('/pronos')
@login_required
def pronos():
    current_user_league_list = get_current_user_league_list()
    return render_template('pronos.html', league_list=current_user_league_list, leagueid=0)


@auth.route('/pronos_show_league/<leaguename>', methods=['POST'])
@login_required
def pronos_show_league(leaguename):
    leagueid = get_leagueid_from_leaguename(leaguename)
    current_user_league_list = get_current_user_league_list()
    games = Game.query.filter_by(leagueid=leagueid).order_by(Game.game_datetime).all()
    records = [u.__dict__ for u in games]
    for r in records:
        r.pop('_sa_instance_state')

    return render_template('pronos.html', league_list=current_user_league_list, leaguename=leaguename,
                           leagueid=leagueid, records=records)


@auth.route('/classements')
@login_required
def classements():
    current_user_league_list = get_current_user_league_list()
    return render_template('classements.html', league_list=current_user_league_list, leagueid=0)


@auth.route('/classements_show_ranking/<leaguename>', methods=['POST'])
@login_required
def classements_show_ranking(leaguename):
    leagueid = get_leagueid_from_leaguename(leaguename)
    current_user_league_list = get_current_user_league_list()
    query = (select(User.id, User.name
                    , GameProno.gameid, GameProno.prono_team_1, GameProno.prono_team_2
                    , Game.score_team_1, Game.score_team_2, Game.bo
                    )
             .join(GameProno, User.id == GameProno.userid)
             .join(Game, Game.id == GameProno.gameid)
             .where(Game.leagueid == leagueid)
             )

    pronos = db.session.execute(query).all()
    pronos = pd.DataFrame(pronos, columns=['userid', 'username', 'gameid',
                                           'prono_team_1', 'prono_team_2',
                                           'score_team_1', 'score_team_2','bo'])
    recap_score = create_standing_table(pronos)

    titles = ['Pseudo', 'Bons pronos', 'Pronos exacts', 'Points']
    return render_template('classements.html', leagueid=leagueid, league_list=current_user_league_list,
                           recap_score=recap_score,
                           titles=titles)




@auth.route('/admin')
@login_required
def admin():
    if current_user.email not in allowed_admin_account:
        return redirect(url_for('main.index'))
    else:
        return render_template("admin.html")


def verification_file_upload(request_file, file_type):
    if file_type not in request_file:
        return redirect(url_for('auth.admin'))
    file = request.files[file_type]
    if file.filename == '':
        return redirect(url_for('auth.admin'))
    if file.filename[-3:] != 'csv':
        return redirect(url_for('auth.admin'))
    file_stream = io.BytesIO(file.read())
    return pd.read_csv(file_stream).to_dict("records")

@auth.route('/admin_add_games', methods=['POST'])
@login_required
def admin_add_games():
    games_to_load_in_database = verification_file_upload(request.files, 'gamesdata')

    for game in games_to_load_in_database:
        # check if game already exist then delete to overwrite:
        check_exist = {}
        row = Game.query.filter(
            Game.game_datetime <= datetime.fromisoformat(game['game_datetime']) + timedelta(minutes=1),
            Game.game_datetime >= datetime.fromisoformat(game['game_datetime']) - timedelta(minutes=1),
            Game.team_1 == game['team_1'],
            Game.team_2 == game['team_2']
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
            game_datetime=datetime.fromisoformat(game['game_datetime']),
            team_1=game['team_1'],
            team_2=game['team_2'],
            score_team_1=game['score_team_1'],
            score_team_2=game['score_team_2']
        )
        if check_exist.get('gameid'):
            new_game.id = check_exist.get('gameid')
        # add the new user to the database
        db.session.add(new_game)
        db.session.commit()

    return render_template('admin.html')


@auth.route('/admin_add_leagues', methods=['POST'])
@login_required
def admin_add_leagues():
    leagues_to_load_in_database = verification_file_upload(request.files, 'leaguesdata')

    for league in leagues_to_load_in_database:
        check_exist = {}
        row = League.query.filter(League.id == league['id']).first()
        if row:
            check_exist['id'] = row.id
            print("suppression enregistrement")
            # delete the league in database
            db.session.delete(row)
            db.session.commit()
        # create a game with the csv data.
        new_league = League(leaguename=league['leaguename'])
        if check_exist.get('id'):
            new_league.id = check_exist.get('id')
        # add the new user to the database
        db.session.add(new_league)
        db.session.commit()
    return redirect(url_for('auth.admin'))


@auth.route('/admin_show_games')
@login_required
def admin_show_games():
    if current_user.email not in allowed_admin_account:
        return redirect(url_for('main.index'))
    else:
        query = (select(Game.id, Game.leagueid,
                         Game.bo, Game.game_datetime,
                        Game.team_1, Game.team_2,
                        Game.score_team_1, Game.score_team_2))
        games = pd.DataFrame(db.session.execute(query).all())
        print(games)
        columns = games.columns
        return render_template("admin_show_games.html", bos=games.to_dict("records"), titles=columns)


@auth.route('/admin_delete_game', methods=['POST'])
@login_required
def admin_delete_game():
    to_delete = request.form.getlist("todelete")
    to_delete = [int(e) for e in to_delete]
    print(to_delete)
    for idd in to_delete:
        row = Game.query.filter(Game.id == idd).first()
        db.session.delete(row)
        db.session.commit()
    return redirect(url_for('auth.admin'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
