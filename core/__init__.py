from flask import Flask, request, render_template, redirect, url_for, g
from extensions import bcrypt, auth, oidc
from models import session as dbsession
from schema import auth_required_schema, schema
from dotenv import load_dotenv
import os
from keycloak import KeycloakOpenID

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET')
app.config.update({
    'SECRET_KEY': os.getenv('SECRET'),
    'TESTING': True,
    'DEBUG': True,
    'OIDC_CLIENT_SECRETS': 'core/client_secrets.json',
    'OIDC_ID_TOKEN_COOKIE_SECURE': False,
    'OIDC_REQUIRE_VERIFIED_EMAIL': False,
    'OIDC_USER_INFO_ENABLED': True,
    'OIDC_OPENID_REALM': 'flask_api',
    'OIDC_SCOPES': ['openid', 'email'],
    'OIDC_TOKEN_TYPE_HINT': 'access_token',
    'OIDC_INTROSPECTION_AUTH_METHOD': 'client_secret_post'
})

bcrypt.init_app(app)
auth.init_app(app)
oidc.init_app(app)

keycloak_openid = KeycloakOpenID(server_url="http://localhost:8080/",
                                 client_id="flask_api",
                                 realm_name="todo",
                                 client_secret_key="LttRP7cGMeCb3juwpoIqqqPiruPv0aEJ",
                                 verify=True)


@app.route('/')
@oidc.require_login
def index():
    query = """
        mutation GetUser($email: String!) {
            getUser(email: $email) {
                user {
                    name
                    notes {
                        id
                        title
                        body
                    }
                }
            }
        }
        """
    variables = {
        "email": oidc.user_getinfo(['email']).get('email')
    }
    result = auth_required_schema.execute(query, variables=variables)
    return render_template("index.html", user=result.data['getUser']['user'])


@app.route('/logout')
def logout():
    refresh_token = oidc.get_refresh_token()
    g.oidc_id_token = None
    oidc.logout()
    redirect(url_for('logout'))
    if refresh_token is not None:
        keycloak_openid.logout(refresh_token)
    return redirect(url_for('index'))


@oidc.accept_token(require_token=True)
@app.route('/add', methods=['POST'])
def addNote():
    query = """
        mutation AddNote($email: String!, $body: String!, $title: String!){
            addNote(email: $email, body: $body, title: $title){
                note{
                    title
                }
            }
        }
    """
    variables = {
        "email": oidc.user_getinfo(['email']).get('email'),
        "title": request.form.get("title"),
        "body": request.form.get("body")
    }
    auth_required_schema.execute(query, variables=variables)
    return redirect(url_for('index'))


@oidc.accept_token(require_token=True)
@app.route('/delete', methods=['POST'])
def deleteNote():
    query = """
        mutation DeleteNote($noteIds: [Int]!) {
            deleteNote(noteIds: $noteIds) {
                note {
                    body
                }
            }
        }
    """
    variables = {"noteIds": request.form.getlist("noteid")}
    auth_required_schema.execute(query, variables=variables)
    return redirect(url_for('index'))


@oidc.accept_token(require_token=True)
@app.route('/update', methods=['POST'])
def updateNote():
    query = """
        mutation UpdateNote($noteId: Int!, $title: String, $body: String) {
            updateNote(noteId: $noteId, title: $title, body: $body) {
                note {
                    title
                    body
                }
            }
        }
    """
    variables = {
        "noteId": request.form.get("noteid"),
        "body": request.form.get("body")
    }
    auth_required_schema.execute(query, variables=variables)
    return redirect(url_for('index'))


@app.teardown_appcontext
def shutdown_session(exception=None):
    dbsession.remove()
