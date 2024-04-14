from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User, UserLeague, Game, GameProno, League, UserTableLocked
from flask_login import login_user, logout_user, login_required, current_user
from . import db
from sqlalchemy import select
import pandas as pd
import numpy as np
import io
from datetime import datetime, timedelta

auth = Blueprint('auth', __name__)

def redirect_not_allowed_admin_account(func):
    def wrapper():
        allowed_admin_account = ('skiaa@hotmail.com', 'zayedlewis@hotmail.com')
        if current_user.email not in allowed_admin_account:
            return redirect(url_for('main.index'))
        else:
            return func()
    wrapper.__name__ = func.__name__
    return wrapper


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

    # check if new signup is locked
    locked = UserTableLocked.query.filter(UserTableLocked.status == 1).first()
    if locked:
        flash(
            "L'inscription de nouveaux utilisateurs est actuellement verrouillée, contactez un admin ou utilisez un compte existant.")
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
    games = Game.query.filter_by(leagueid=leagueid).order_by(Game.gamedatetime).all()
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
                    , GameProno.gameid, GameProno.team1prono, GameProno.team2prono
                    , Game.team1score, Game.team2score
                    )
             .join(GameProno, User.id == GameProno.userid)
             .join(Game, Game.id == GameProno.gameid)
             .where(Game.leagueid == leagueid)
             )

    pronos = db.session.execute(query).all()
    pronos = pd.DataFrame(pronos, columns=['userid', 'username', 'gameid',
                                           'team1prono', 'team2prono',
                                           'team1score', 'team2score'])
    pronos['prono_team_win'] = np.where(
        (pronos['team1prono'] > pronos['team2prono']) & (pronos['team1prono'] != pronos['team2prono']), 'team1',
        'team2')
    pronos['score_team_win'] = np.where(
        (pronos['team1score'] > pronos['team2score']) & (pronos['team1score'] != pronos['team2score']), 'team1',
        'team2')
    pronos['bon_prono'] = np.where(pronos['prono_team_win'] == pronos['score_team_win'], 1, 0)
    pronos['score_exact'] = np.where(
        (pronos['team1prono'] == pronos['team1score']) & (pronos['team2prono'] == pronos['team2score']), 1, 0)
    pronos['points'] = pronos['bon_prono'] + pronos['score_exact']

    recap_score = pronos[['userid', 'username', 'bon_prono', 'score_exact', 'points']].groupby(
        ['userid', 'username']).sum()
    recap_score = recap_score.sort_values('points', ascending=False)
    recap_score = recap_score.reset_index(level=['userid', 'username'])
    recap_score = recap_score.drop(columns=['userid']).to_dict("records")

    titles = ['Pseudo', 'Bons pronos', 'Pronos exacts', 'Points']
    return render_template('classements.html', leagueid=leagueid, league_list=current_user_league_list,
                           recap_score=recap_score,
                           titles=titles)


@auth.route('/admin')
@login_required
@redirect_not_allowed_admin_account
def admin():
    query = UserTableLocked.query.filter(UserTableLocked.id == 1).first()
    if query:
        status = bool(query.status)
    else:
        status = 0
    return render_template("admin.html", signup_locked=status)


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
@redirect_not_allowed_admin_account
def admin_add_games():
    games_to_load_in_database = verification_file_upload(request.files, 'gamesdata')

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


@auth.route('/admin_add_leagues', methods=['POST'])
@login_required
@redirect_not_allowed_admin_account
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
@redirect_not_allowed_admin_account
def admin_show_games():
    return admin_show_table(query=(select(Game.id, Game.leagueid,
                                          Game.bo, Game.gamedatetime,
                                          Game.team1, Game.team2,
                                          Game.team1score, Game.team2score)),
                            html_template="admin_show_games.html")


@auth.route('/admin_show_leagues')
@login_required
@redirect_not_allowed_admin_account
def admin_show_leagues():
    return admin_show_table(query=(select(League.id, League.leaguename)), html_template="admin_show_leagues.html")


@auth.route('/admin_show_users')
@login_required
@redirect_not_allowed_admin_account
def admin_show_users():
    return admin_show_table(query=(select(User.id, User.name, User.email)), html_template="admin_show_users.html")


def admin_show_table(query, html_template):
    df = pd.DataFrame(db.session.execute(query).all())
    return render_template(html_template, data=df.to_dict("records"), titles=df.columns)


@auth.route('/admin_delete_game', methods=['POST'])
@login_required
@redirect_not_allowed_admin_account
def admin_delete_game():
    return admin_delete_from(Game)


@auth.route('/admin_delete_league', methods=['POST'])
@login_required
@redirect_not_allowed_admin_account
def admin_delete_league():
    return admin_delete_from(League)


@auth.route('/admin_delete_user', methods=['POST'])
@login_required
@redirect_not_allowed_admin_account
def admin_delete_user():
    return admin_delete_from(User)


def admin_delete_from(table):
    to_delete = request.form.getlist("todelete")
    to_delete = [int(e) for e in to_delete]
    for idd in to_delete:
        row = table.query.filter(table.id == idd).first()
        db.session.delete(row)
        db.session.commit()
    return redirect(url_for('auth.admin'))


@auth.route('/admin_lock_signup', methods=['POST'])
@login_required
@redirect_not_allowed_admin_account
def admin_lock_signup():
    signup_status = int(bool(request.form.get("signup_status")))
    row = UserTableLocked.query.filter(UserTableLocked.status == signup_status).first()
    if not row:
        to_delete = UserTableLocked.query.filter(UserTableLocked.id == 1).first()
        if to_delete:
            db.session.delete(to_delete)
            db.session.commit()

        new_status = UserTableLocked(id=1, status=signup_status)
        db.session.add(new_status)
        db.session.commit()

    return redirect(url_for('auth.admin'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
