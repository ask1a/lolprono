from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from .models import User, UserLeague, Game, GameProno, League, UserTableLocked, Teams
from flask_login import login_user, logout_user, login_required, current_user
from . import db
from sqlalchemy import select, and_, update
import pandas as pd
import numpy as np
import io
from datetime import datetime, timedelta
from .utils import create_standing_table, create_points_dataframe, eval_team_win

auth = Blueprint('auth', __name__)


def common_entries(*dcts):
    # function used to combine several dictionaries into a list of tuple using list() with common key on first tuple index
    if not dcts:
        return
    for i in set(dcts[0]).intersection(*dcts[1:]):
        yield (i,) + tuple(d[i] for d in dcts)


def redirect_not_allowed_admin_account(func):
    def wrapper():
        allowed_admin_account = ('skiaa@hotmail.com', 'zayedlewis@hotmail.com', 'test@test.fr')
        if current_user.email not in allowed_admin_account:
            return redirect(url_for('main.index'))
        else:
            return func()

    wrapper.__name__ = func.__name__
    return wrapper


@auth.route('/delete_usertest_post', methods=['POST'])
@login_required
@redirect_not_allowed_admin_account
def delete_usertest_post():
    email = request.form.get('email')
    row = User.query.filter(User.email == email).first()
    if row:
        db.session.delete(row)
        db.session.commit()
        return 'ok'
    return 'ko'


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
    flash("Inscription réussie! 👍")
    # code to validate and add user to database goes here
    return redirect(url_for('auth.login'))


@auth.route('/ligues')
@login_required
def ligues():
    return render_template('ligues.html',
                           league1=is_registered_in_league(1),
                           league2=is_registered_in_league(2),
                           league3=is_registered_in_league(3))


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
    flash('Ligue ajoutée! 🥳')
    return redirect(url_for('auth.ligues'))


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


@auth.route('/ligue_msi_2024', methods=['POST'])
@login_required
def ligue_msi_2024_post():
    userid = current_user.id
    leagueid = 3
    leaguename = "Mid-Season Invitational 2024"

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


@auth.route('/pronos_update/<leaguename>', methods=['POST'])
@login_required
def pronos_update(leaguename):
    heure_prono = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    pronos_joueur = dict(request.form)
    pronos_team1 = {k.split(';')[1]: v for k, v in pronos_joueur.items() if 't1' in k}
    pronos_team2 = {k.split(';')[1]: v for k, v in pronos_joueur.items() if 't2' in k}
    pronos_bo = {k.split(';')[1]: k.split(';')[3] for k, v in pronos_joueur.items() if 't1' in k}
    heure_pronos = {k.split(';')[1]: k.split(';')[2] for k, v in pronos_joueur.items() if 't1' in k}
    # creation of a list of tuples containing all the information needed to check before puting the score
    # in the database (gameid, score1, score2, bo and datetime)
    pronos_teams = list(common_entries(pronos_team1, pronos_team2, pronos_bo, heure_pronos))

    for prono in pronos_teams:
        # skip incomplete prono
        if '' in prono:
            continue
        # verification of the score and time of the bet
        if ((int(prono[1]) + int(prono[2]) <= int(prono[3])) and
                ((int(prono[1]) == (int(prono[3]) // 2 + 1)) or (int(prono[2]) == (int(prono[3]) // 2 + 1))) and
                (datetime.strptime(heure_prono, '%Y-%m-%d %H:%M:%S') < datetime.strptime(prono[4], '%Y-%m-%d %H:%M:%S'))
        ):
            # check if there is an existing prediction for this user and this game
            row = GameProno.query.filter_by(userid=current_user.id, gameid=prono[0]).first()

            if row:
                # Update existing prediction
                db.session.execute(
                    update(GameProno)
                    .where(GameProno.userid == current_user.id)
                    .where(GameProno.gameid == prono[0])
                    .values(prono_team_1=int(prono[1]), prono_team_2=int(prono[2]))
                )
                flash("Pronostic mis à jour! 👌")
            else:
                # Add new prediction
                new_prono = GameProno(userid=current_user.id, gameid=prono[0], prono_team_1=int(prono[1]),
                                      prono_team_2=int(prono[2]))
                db.session.add(new_prono)
                flash("Pronostic mis à jour! 👌")
            db.session.commit()
        else:
            flash("🧐 Erreur, ton pronostic est invalide, pense à bien tenir compte du type de BO 👨‍🏫.")

    return redirect(url_for('auth.pronos_show_league', leaguename=leaguename), 307)


@auth.route('/pronos_show_league/<leaguename>', methods=['POST'])
@login_required
def pronos_show_league(leaguename):
    leagueid = get_leagueid_from_leaguename(leaguename)
    current_user_league_list = get_current_user_league_list()
    query = (select(User.id.label("userid"), User.name.label("username")
                    , Game.score_team_1, Game.score_team_2, Game.leagueid, Game.bo
                    , Game.game_datetime, Game.team_1, Game.team_2, Game.id.label("gameid")
                    , GameProno.prono_team_1, GameProno.prono_team_2
                    )
             .join(UserLeague, UserLeague.userid == User.id)
             .join(Game, UserLeague.leagueid == Game.leagueid)
             .join(GameProno, and_(GameProno.userid == User.id, GameProno.gameid == Game.id), isouter=True)
             .where(Game.leagueid == leagueid)
             .where(current_user.id == User.id)
             .order_by(Game.game_datetime.desc())
             )
    pronos_form = db.session.execute(query).all()
    records = []
    if pronos_form:
        pronos_form = pd.DataFrame(pronos_form)
        pronos_form['editable'] = datetime.now() < pronos_form["game_datetime"]
        pronos_form = pronos_form.replace(r'^\s*$', np.nan, regex=True)
        pronos_form = pronos_form.fillna(0)

        columns_to_integer = ['score_team_1', 'score_team_2', 'prono_team_1', 'prono_team_2']

        query = (select(User.id, User.name
                        , GameProno.gameid, GameProno.prono_team_1, GameProno.prono_team_2
                        , Game.score_team_1, Game.score_team_2, Game.bo
                        )
                 .join(GameProno, User.id == GameProno.userid)
                 .join(Game, Game.id == GameProno.gameid)
                 .where(Game.leagueid == leagueid)
                 )

        table_points = db.session.execute(query).all()
        table_points = pd.DataFrame(table_points, columns=['userid', 'username', 'gameid',
                                                           'prono_team_1', 'prono_team_2',
                                                           'score_team_1', 'score_team_2', 'bo'])
        table_points = create_points_dataframe(table_points)
        table_points = table_points.replace(r'^\s*$', np.nan, regex=True)
        table_points = table_points.fillna(0)

        for col in columns_to_integer:
            pronos_form[col] = pronos_form[col].astype('Int64')
            table_points[col] = table_points[col].astype('Int64')
        pronos_form = pd.merge(pronos_form, table_points,
                               on=['userid', 'username', 'gameid', 'prono_team_1', 'prono_team_2', 'score_team_1',
                                   'score_team_2', 'bo'], how='left')
        pronos_form = pronos_form.drop(columns='score_team_win')
        pronos_form['score_team_win'] = eval_team_win(pronos_form, 'score_team_1', 'score_team_2')
        pronos_form = pronos_form.fillna(0)

        records = pronos_form.to_dict("records")

        # ajout des logos dans l'item records
        query = (select(Teams.long_label, Teams.logo_url))
        logos = db.session.execute(query).all()
        logos = pd.DataFrame(logos, columns=['long_label', 'logo_url'])
        logos = logos.set_index('long_label')['logo_url'].to_dict()
        for item in records:
            item['logo_team_1'] = logos.get(item.get('team_1'))
            item['logo_team_2'] = logos.get(item.get('team_2'))

    return render_template('pronos.html', league_list=current_user_league_list, leaguename=leaguename,
                           leagueid=leagueid, records=records, datetime=datetime)


@auth.route('/pronos_resume/<gameid>', methods=['POST'])
@login_required
def show_game_pronos(gameid):
    query = (select(User.id, User.name
                    , GameProno.gameid, GameProno.prono_team_1, GameProno.prono_team_2
                    , Game.score_team_1, Game.score_team_2, Game.bo
                    , Game.team_1, Game.team_2
                    , League.id, League.leaguename
                    )
             .join(GameProno, User.id == GameProno.userid)
             .join(Game, Game.id == GameProno.gameid)
             .join(League, Game.leagueid == League.id)
             .where(Game.id == gameid)
             )

    pronos = db.session.execute(query).all()
    pronos = pd.DataFrame(pronos, columns=['userid', 'username', 'gameid',
                                           'prono_team_1', 'prono_team_2',
                                           'score_team_1', 'score_team_2', 'bo', 'team_1', 'team_2', 'leagueid',
                                           'leaguename'])

    recap_score = create_points_dataframe(pronos)

    liste_a_supprimer = ['userid', 'gameid', 'prono_team_win', 'score_team_win', 'prono_correct', 'score_exact',
                         'nb_pronos_corrects', 'nb_pronos', 'odds', 'score_team_1', 'score_team_2', 'bo', 'team_1',
                         'team_2', 'leagueid', 'leaguename']

    recap_score = recap_score.drop(liste_a_supprimer, axis=1)
    recap_score = recap_score.to_dict("records")

    score_final = {'team_1':pronos['team_1'][0], 'score_team_1':pronos['score_team_1'][0], 'score_team_2':pronos['score_team_2'][0], 'team_2':pronos['team_2'][0],
                   'leaguename':pronos['leaguename'][0]}

    titles = ['Pseudo']
    titles.append(pronos['team_1'][0])
    titles.append(pronos['team_2'][0])
    titles.append('Points')

    return render_template('pronos_resume.html', recap_score=recap_score, titles=titles, score_final=score_final)


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
                                           'score_team_1', 'score_team_2', 'bo'])
    recap_score = create_standing_table(pronos)

    titles = ['Pseudo', 'Bons pronos', 'Pronos exacts', 'Points']
    return render_template('classements.html', leagueid=leagueid, leaguename=leaguename,
                           league_list=current_user_league_list,
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
            Game.game_datetime <= datetime.fromisoformat(game['game_datetime']) + timedelta(minutes=1),
            Game.game_datetime >= datetime.fromisoformat(game['game_datetime']) - timedelta(minutes=1),
            Game.team_1 == game['team_1'],
            Game.team_2 == game['team_2']
        ).first()
        if row:
            check_exist['gameid'] = row.id
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
        flash("Fichier de bo ajouté!")
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
        flash("Fichier de league ajouté!")
    return redirect(url_for('auth.admin'))


@auth.route('/admin_show_games')
@login_required
@redirect_not_allowed_admin_account
def admin_show_games():
    return admin_show_table(query=(select(Game.id, Game.leagueid,
                                          Game.bo, Game.game_datetime,
                                          Game.team_1, Game.team_2,
                                          Game.score_team_1, Game.score_team_2)),
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
        flash("Statut de verrouillage mis à jour!")

    return redirect(url_for('auth.admin'))


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.index'))
