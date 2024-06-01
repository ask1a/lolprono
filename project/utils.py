import numpy as np
import pandas as pd
import random
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from . import db
from .models import SignupCode
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv(".env")


def create_standing_table(pronos: pd.DataFrame) -> list:
    pronos['prono_team_win'] = np.where(
        (pronos['prono_team_1'] > pronos['prono_team_2']) & (pronos['prono_team_1'] != pronos['prono_team_2']),
        'team_1',
        'team_2')
    pronos['score_team_win'] = np.where(
        (pronos['score_team_1'] > pronos['score_team_2']) & (pronos['score_team_1'] != pronos['score_team_2']),
        'team_1',
        'team_2')
    pronos['prono_correct'] = np.where(pronos['prono_team_win'] == pronos['score_team_win'], 1, 0)
    pronos['score_exact'] = np.where(
        (pronos['prono_team_1'] == pronos['score_team_1']) & (pronos['prono_team_2'] == pronos['score_team_2']), 1, 0)

    game_odds = pronos[['gameid', 'prono_correct']].groupby(['gameid']).agg(['sum', 'count']).reset_index().values
    game_odds = pd.DataFrame(game_odds, columns=['gameid', 'nb_pronos_corrects', 'nb_pronos'])
    game_odds['odds'] = game_odds['nb_pronos'] / game_odds['nb_pronos_corrects']

    pronos = pronos.merge(game_odds, on='gameid')
    pronos['points'] = np.where(pronos['score_exact'] == 1, pronos['odds'] * (pronos['bo'] // 2 + 1), pronos['odds'])
    pronos['points'] = np.where(pronos['prono_correct'] == 1, pronos['points'], 0)

    recap_score = pronos[['userid', 'username', 'prono_correct', 'score_exact', 'points']].groupby(
        ['userid', 'username']).sum()
    recap_score = recap_score.sort_values('points', ascending=False)
    recap_score = recap_score.reset_index(level=['userid', 'username'])
    recap_score = recap_score.drop(columns=['userid']).to_dict("records")
    return recap_score


def random_digit() -> str:
    return str(random.choice(list(range(10))))


def validation_email_body(code: str) -> str:
    return "Code de validation : " + code


def write_signup_code(email: str, code: str) -> None:
    row = SignupCode.query.filter(SignupCode.email == email).first()
    if row:
        db.session.delete(row)
        db.session.commit()

    new_code = SignupCode(email=email, code=code, expire_datetime=datetime.today() + timedelta(minutes=2))
    db.session.add(new_code)
    db.session.commit()
    return None


def send_email_validation(mail_to: str, testing=None) -> None:
    code = ''.join([random_digit() for i in range(6)])
    if testing is None:
        send_email(mail_to, "Votre code de validation d'inscription.", validation_email_body(code))
    write_signup_code(mail_to, code)
    return None



def send_email(mail_to, mail_subject, mail_body, sender_email=os.getenv('EMAIL_LOGIN'), smtp_server='ssl0.ovh.net',
            smtp_port=587, smtp_login=os.getenv('EMAIL_LOGIN'), smtp_password=os.getenv('EMAIL_PWD')):
    # Création de l'objet message
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = mail_to
    msg['Subject'] = mail_subject

    # Ajout du corps de l'email
    msg.attach(MIMEText(mail_body, 'plain'))

    # Connexion au serveur SMTP d'OVH et envoi de l'email
    server = smtplib.SMTP(smtp_server, smtp_port)
    server.starttls()  # Sécurisation de la connexion
    server.login(smtp_login, smtp_password)  # Authentification
    server.sendmail(sender_email, mail_to, msg.as_string())
    server.quit()


