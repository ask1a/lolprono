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


def test_signup_success(client):
    response = client.post("/signup", data={
        "email": "test@test.fr",
        "name": "test",
        "password": "test"
    }, follow_redirects=True)
    assert response.text.__contains__("Connectez-vous :")


def test_signup_fail(client):
    response = client.post("/signup", data={
        "email": "test@test.fr",
        "name": "test",
        "password": "test"
    }, follow_redirects=True)
    assert response.text.__contains__("email existe déjà en base de donnée!")


def login(client):
    return client.post('/login', data={
        "email": "test@test.fr",
        "password": "test"
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


def test_profile_loadpage(client):
    assert login(client).status_code == 200
    response = client.get("/profile", data={
        "email": "test@test.fr",
        "password": "test"
    }, follow_redirects=True)
    assert response.text.__contains__("Bienvenu, test!")


def test_delete_usertest(client):
    response = client.post("/delete_usertest_post")
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
