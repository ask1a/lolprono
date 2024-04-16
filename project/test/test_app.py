import pytest

from project import create_app
from project.auth import delete_usertest_post

app_test = create_app('testing')


@pytest.fixture
def client():
    with app_test.test_client() as client:
        yield client


def test_index_loadpage(client):
    response = client.get("/index")
    assert response.status_code == 200


def test_signup_loadpage(client):
    response = client.get("/signup")
    assert response.status_code == 200


def test_signup_success(client, email="test@test.fr", name="test", password="test"):
    response = client.post("/signup", data={
        "email": email,
        "name": name,
        "password": password
    }, follow_redirects=True)
    assert response.text.__contains__("Connectez-vous :")


def test_signup_fail(client):
    response = client.post("/signup", data={
        "email": "test@test.fr",
        "name": "test",
        "password": "test"
    }, follow_redirects=True)
    assert response.text.__contains__("email existe déjà en base de donnée!")


def signup(client, email="test@test.fr", name="test", password="test"):
    return client.post("/signup", data={
        "email": email,
        "name": name,
        "password": password
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
    assert response.text.__contains__("Bienvenu, test!")


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
    assert response.text.__contains__("Resultats & pronostics")


def test_pronos_loadpage(client):
    assert login(client).status_code == 200
    response = client.get("/pronos", follow_redirects=True)
    assert response.text.__contains__("Resultats & pronostics")


def test_pronos_show_league(client):
    assert login(client).status_code == 200
    response = client.post("/pronos_show_league/LEC spring 2024", follow_redirects=True)
    assert response.text.__contains__("Matchs du LEC spring 2024")


def test_classements_loadpage(client):
    assert login(client).status_code == 200
    response = client.get("/classements", follow_redirects=True)
    assert (response.text.__contains__("Classement")) and (
        response.text.__contains__("Selectionnez une ligue")) and not (
        response.text.__contains__("Resultats & pronostics"))


def test_classements_show_ranking(client):
    assert login(client).status_code == 200
    response = client.post("/classements_show_ranking/LEC spring 2024", follow_redirects=True)
    assert response.text.__contains__("Pronos exacts")


def test_profile_loadpage(client):
    assert login(client).status_code == 200
    response = client.get("/profile", follow_redirects=True)
    assert response.text.__contains__("Bienvenu, test!")


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
    response = client.post("/admin_lock_signup", data={"signup_status":True}, follow_redirects=True)
    assert (response.text.__contains__("Admin")) and (response.text.__contains__("Statut de verrouillage mis à jour!"))


def test_admin_lock_signup_no(client):
    assert login(client).status_code == 200
    response = client.post("/admin_lock_signup", data={}, follow_redirects=True)
    assert (response.text.__contains__("Admin")) and (response.text.__contains__("Statut de verrouillage mis à jour!"))


def test_admin_loadpage_not_allowed(client):
    assert signup(client, 't@t.fr', 't', 't').status_code == 200
    assert login(client, 't@t.fr', 't').status_code == 200
    response = client.get("/admin", follow_redirects=True)
    assert response.text.__contains__("ça a commencé?")


def test_delete_usertest(client):
    response = client.post("/delete_usertest_post" ,data={"email": "test@test.fr"})
    assert response.text == 'ok'

def test_delete_usertest2(client):
    response = client.post("/delete_usertest_post", data={"email": "t@t.fr"})
    assert response.text == 'ok'

# def test_login_logout(client):
#     """Make sure login and logout works."""
#     print(dir(client))
#     email = client.app.config["test@test.fr"]
#     password = client.app.config["test"]
#
#     rv = login(client)
#     assert rv.status_code == 200

# def test_index_profile(client):
#     response = client.get("/profile")
#     assert response.status_code == 200
