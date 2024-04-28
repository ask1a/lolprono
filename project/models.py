from flask_login import UserMixin
from . import db
import pandas as pd
from sqlalchemy import update


class User(UserMixin, db.Model):
    """Manage users infos"""
    id = db.Column(db.Integer, primary_key=True)  # primary keys are required by SQLAlchemy
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    name = db.Column(db.String(1000))

class UserTableLocked(db.Model):
    """Manage users infos"""
    id = db.Column(db.Integer, primary_key=True)  # primary keys are required by SQLAlchemy
    status = db.Column(db.Integer, unique=False)


class League(db.Model):
    """Manage leagues infos"""
    id = db.Column(db.Integer, primary_key=True)  # primary keys are required by SQLAlchemy
    leaguename = db.Column(db.String(50), unique=False)

class UserLeague(db.Model):
    """Manage users's leagues"""
    id = db.Column(db.Integer, primary_key=True)  # primary keys are required by SQLAlchemy
    userid = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    leagueid = db.Column(db.Integer, unique=False)
    leaguename = db.Column(db.String(50), unique=False)

class Game(db.Model):
    """Manage games infos"""
    id = db.Column(db.Integer, primary_key=True)  # primary keys are required by SQLAlchemy
    leagueid = db.Column(db.Integer, unique=False, nullable=False)
    bo = db.Column(db.Integer, unique=False, nullable=False)
    game_datetime = db.Column(db.DateTime, unique=False, nullable=False)
    team_1 = db.Column(db.String(50), unique=False, nullable=True)
    team_2 = db.Column(db.String(50), unique=False, nullable=True)
    score_team_1 = db.Column(db.Integer, unique=False, nullable=True)
    score_team_2 = db.Column(db.Integer, unique=False, nullable=True)

class GameProno(db.Model):
    """Manage games infos"""
    id = db.Column(db.Integer, primary_key=True)  # primary keys are required by SQLAlchemy
    userid = db.Column(db.Integer, db.ForeignKey('user.id'), unique=False, nullable=False)
    gameid = db.Column(db.Integer, db.ForeignKey('game.id'), unique=False, nullable=False)
    prono_team_1 = db.Column(db.Integer, unique=False, nullable=True)
    prono_team_2 = db.Column(db.Integer, unique=False, nullable=True)

class Teams(db.Model):
    """Manage teams infos"""
    id = db.Column(db.Integer, primary_key=True)  # primary keys are required by SQLAlchemy
    short_label = db.Column(db.String(10), unique=True, nullable=False)
    long_label = db.Column(db.String(50), unique=True, nullable=False)
    region_league = db.Column(db.String(20), unique=False, nullable=False)
    logo_url = db.Column(db.String(20), unique=True, nullable=False)

def add_teams_values(*args, **kwargs):
    #insert teams
    teams_table = pd.read_csv('project/SQL_scripts/table_teams.csv')
    print(teams_table)
    for row in teams_table.values:
        if Teams.query.filter(Teams.id==row[0]).first():
            db.session.execute(update(Teams).where(Teams.id == row[0]).values(short_label=row[1], long_label=row[2], region_league=row[3], logo_url=row[4]))
        else:
            to_add = Teams(id=row[0], short_label=row[1], long_label=row[2], region_league=row[3], logo_url=row[4])
            db.session.add(to_add)
        db.session.commit()
