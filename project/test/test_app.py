import pytest
import os

from project import create_app
import pandas as pd

from ..models import SignupCode

app_test = create_app('testing')

g2_win_expected_html = """                    <div class="column is-size-5">2024-04-07 17:00:00 (BO5)</div>
                    <div class="column">
                        <img src="/static/logos/g2.png" alt="G2 Esports" style="width: auto; height: 50px;">
                    </div>
                    
                    <div class="column is-size-5 has-text-weight-bold">G2 Esports ✅</div>
"""


@pytest.fixture
def client():
    with app_test.test_client() as client:
        yield client


@pytest.fixture(scope='session')
def csv_gamesdata(tmpdir_factory):
    pd.DataFrame(
        {'id': [1, 22],'leagueid': [1, 1], 'bo': [5, 3], 'game_datetime': ['2024-04-07T17:00:00', '2034-04-07T17:00:00'],
         'team_1': ['G2 Esports', 'GiantX'],
         'team_2': ['Team BDS', 'Fnatic'],
         'score_team_1': [3, None], 'score_team_2': [1, None]}).to_csv('./game_table_exemple.csv', index=False)
    gamesdata = "./game_table_exemple.csv"
    return (open(gamesdata, 'rb'), gamesdata)


@pytest.fixture(scope='session')
def csv_leaguesdata(tmpdir_factory):
    pd.DataFrame({'id': [1, 2], 'leaguename': ['LEC spring 2024', 'LEC summer 2024']}).to_csv(
        './league_table_exemple.csv', index=False)
    leaguesdata = "./league_table_exemple.csv"
    return (open(leaguesdata, 'rb'), leaguesdata)


def test_index_loadpage(client):
    response = client.get("/index")
    assert response.status_code == 200


def test_signup_loadpage(client):
    response = client.get("/signup")
    assert response.status_code == 200


def test_signup_success(client, email="test@test.fr", name="test", password="test"):
    response = client.post("/signup_post", data={
        "email": email,
        "name": name,
        "password": password,
        "testing": 1
    }, follow_redirects=True)
    assert response.text.__contains__("Rentrez le code de validation envoyé par email")


def test_signup_validation_loadpage(client, email='test@test.fr'):
    assert signup(client).status_code == 200
    response = signup_validation(client, email, 'test', 'test', 1)
    assert response.text.__contains__("Connectez-vous")


def signup_validation(client, email, name, password, testing):
    row = SignupCode.query.filter(SignupCode.email == email).first()
    code = row.code
    response = client.post("/signup_validation",
                           data={"code": code, "email": email, "name": name, "password": password, 'testing': testing},
                           follow_redirects=True)
    return response


def test_signup_fail(client):
    response = client.post("/signup_post", data={
        "email": "test@test.fr",
        "name": "test",
        "password": "test",
        "testing": 1
    }, follow_redirects=True)
    assert response.text.__contains__("email existe déjà en base de donnée!")


def signup(client, email="test@test.fr", name="test", password="test",testing=1):
    return client.post("/signup_post", data={
        "email": email,
        "name": name,
        "password": password,
        "testing" : testing
    }, follow_redirects=True)


def login(client, email="test@test.fr", password="test"):
    return client.post('/login', data={
        "email": email,
        "password": password
    }, follow_redirects=True)


def test_login_loadpage(client):
    response = client.get("/login")
    assert response.status_code == 200


def test_login_success(client):
    response = client.post("/login", data={
        "email": "test@test.fr",
        "password": "test"
    }, follow_redirects=True)
    assert response.text.__contains__("Bienvenue, test!")


def test_login_fail(client):
    response = client.post("/login", data={
        "email": "test@test.fr",
        "password": "badpassword"
    }, follow_redirects=True)
    assert response.text.__contains__("Mauvais identifiants, email et/ou mot de passe incorrects.")


def test_ligues_loadpage(client):
    assert login(client).status_code == 200
    response = client.get("/ligues", follow_redirects=True)
    assert response.text.__contains__("Ajouter la ligue")


def test_ligues_spring_add(client):
    assert login(client).status_code == 200
    response = client.post("/ligue_spring", follow_redirects=True)
    assert response.text.__contains__("Déjà inscrit!")


def test_admin_add_games(client, csv_gamesdata):
    assert login(client).status_code == 200
    response = client.post("/admin_add_games", data={'gamesdata': csv_gamesdata},
                           follow_redirects=True)
    assert response.text.__contains__("Fichier de bo ajouté")

def test_admin_add_leagues(client, csv_leaguesdata):
    assert login(client).status_code == 200
    response = client.post("/admin_add_leagues", data={'leaguesdata': csv_leaguesdata},
                           follow_redirects=True)
    assert response.text.__contains__("Fichier de league ajouté!")

def test_pronos_loadpage(client):
    assert login(client).status_code == 200
    response = client.get("/pronos", follow_redirects=True)
    assert (response.text.__contains__("Résultats & pronostics")) & (response.text.__contains__("LEC spring 2024"))


def test_pronos_show_league(client):
    assert login(client).status_code == 200
    response = client.post("/pronos_show_league/LEC spring 2024", follow_redirects=True)
    assert response.text.__contains__("Matchs du LEC spring 2024")


def test_pronos_update_fail(client):
    assert login(client).status_code == 200
    response = client.post("/pronos_update/LEC spring 2024", data=dict(
        [('gameidt1;6;2034-04-07 17:00:00;3', '0'), ('gameidt2;6;2034-04-07 17:00:00;3', '0')]), follow_redirects=True)
    assert response.text.__contains__("Erreur, ton pronostic est invalide, pense à bien tenir compte du ")


def test_pronos_update_success(client):
    assert login(client).status_code == 200
    response = client.post("/pronos_update/LEC spring 2024", data=dict(
        [('gameidt1;6;2034-04-07 17:00:00;3', '2'), ('gameidt2;6;2034-04-07 17:00:00;3', '0')]), follow_redirects=True)
    assert response.text.__contains__("Pronostic mis à jour!")


def test_admin_update_table_teams(client):
    assert login(client).status_code == 200
    response = client.get("/admin_update_table_teams", follow_redirects=True)
    assert response.status_code == 200


def test_pronos_show_league_team_win_g2(client):
    assert login(client).status_code == 200
    response = client.post("/pronos_show_league/LEC spring 2024", follow_redirects=True)
    assert (response.text.__contains__("Matchs du LEC spring 2024")) & (
        response.text.__contains__(g2_win_expected_html))

def test_pronos_resume_game(client):
    assert login(client).status_code == 200
    response = client.post("/pronos_resume/1", follow_redirects=True)
    assert (response.text.__contains__("Score final"))

def test_classements_loadpage(client):
    assert login(client).status_code == 200
    response = client.get("/classements", follow_redirects=True)
    assert (response.text.__contains__("Classement")) and not (
        response.text.__contains__("Resultats & pronostics"))


def test_classements_show_ranking(client):
    assert login(client).status_code == 200
    response = client.post("/classements_show_ranking/LEC spring 2024", follow_redirects=True)
    assert response.text.__contains__("Pronos exacts")


def test_profile_loadpage(client):
    assert login(client).status_code == 200
    response = client.get("/profile", follow_redirects=True)
    assert response.text.__contains__("Bienvenue, test!")


def test_profile_unsubscribe_league(client):
    assert login(client).status_code == 200
    response = client.post("/profile_unsubscribe_league/LEC spring 2024", follow_redirects=True)
    assert not response.text.__contains__("Se désinscrire")


def test_admin_loadpage_allowed(client):
    assert login(client).status_code == 200
    response = client.get("/admin", follow_redirects=True)
    assert response.text.__contains__("Admin")

def test_admin_show_games_loadpage(client):
    assert login(client).status_code == 200
    response = client.get("/admin_show_games", follow_redirects=True)
    assert (response.text.__contains__("Admin")) and (response.text.__contains__("score"))


def test_admin_show_leagues_loadpage(client):
    assert login(client).status_code == 200
    response = client.get("/admin_show_leagues", follow_redirects=True)
    assert (response.text.__contains__("Admin")) and (response.text.__contains__("leaguename"))


def test_admin_show_users_loadpage(client):
    assert login(client).status_code == 200
    response = client.get("/admin_show_users", follow_redirects=True)
    assert (response.text.__contains__("Admin")) and (response.text.__contains__("email"))


def test_admin_lock_signup_yes(client):
    assert login(client).status_code == 200
    response = client.post("/admin_lock_signup", data={"signup_status": True}, follow_redirects=True)
    assert (response.text.__contains__("Admin")) and (response.text.__contains__("Statut de verrouillage mis à jour!"))


def test_signup_locked(client, email="testlock@test.fr", name="test", password="test"):
    response = client.post("/signup", data={
        "email": email,
        "name": name,
        "password": password
    }, follow_redirects=True)
    assert not response.text.__contains__("Connectez-vous :")


def test_admin_lock_signup_no(client):
    assert login(client).status_code == 200
    response = client.post("/admin_lock_signup", data={}, follow_redirects=True)
    assert (response.text.__contains__("Admin")) and (response.text.__contains__("Statut de verrouillage mis à jour!"))


def test_admin_loadpage_not_allowed(client):
    assert signup(client, 't@t.fr', 'toto', 't',1).status_code == 200
    assert signup_validation(client,'t@t.fr', 'toto', 't',1).status_code == 200
    assert login(client, 't@t.fr', 't').status_code == 200
    response = client.get("/admin", follow_redirects=True)
    assert (response.text.__contains__("ça a commencé?"))


def test_delete_usertest2(client):
    assert login(client).status_code == 200
    response = client.post("/delete_usertest_post", data={"email": "t@t.fr"})
    assert response.text == 'ok'


def test_delete_usertest(client):
    assert login(client).status_code == 200
    response = client.post("/delete_usertest_post", data={"email": "test@test.fr"})
    assert response.text == 'ok'


def test_delete_temp_csvfiles():
    os.remove("./game_table_exemple.csv")
    os.remove("./league_table_exemple.csv")
