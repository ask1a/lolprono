import pytest

from .__init__ import create_app

app_test=create_app()

# app_test.config['DEBUG'] = True
# app_test.config['TESTING'] = True
#
# app_test.config['SECRET_KEY'] = 'secret-key-goes-here'
# app_test.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db_test.sqlite'


@pytest.fixture
def client():
    with app_test.test_client() as client:
        yield client

def test_index_get(client):
    response = client.get("/index")
    assert response.status_code == 200

def test_login_get(client):
    response = client.get("/login")
    assert response.status_code == 200

def test_signup_get(client):
    response = client.get("/signup")
    assert response.status_code == 200

#
# def test_signup_post(client):
#     response = client.post("/signup" , data={
#         "email":"test1@test.fr",
#         "name":"test1",
#         "password":"test1"
#     }, follow_redirects=True)
#     assert response.status_code == 200

def test_login_post(client):
    print(help(client.post))
    response = client.post("/login" , data={
        "email":"test@test.fr",
        "password":"test"
    }, follow_redirects=True)
    assert response.status_code == 200




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
