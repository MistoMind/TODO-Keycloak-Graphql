from flask import Flask, request, render_template, redirect, url_for, g
from extensions import bcrypt, auth, oidc
from models import session as dbsession
from schema import auth_required_schema, schema
from dotenv import load_dotenv
import os
from keycloak import KeycloakOpenID
import stripe

load_dotenv()

app = Flask(__name__)
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
    'OIDC_INTROSPECTION_AUTH_METHOD': 'client_secret_post',
    'STRIPE_PUBLIC_KEY': os.getenv('STRIPE_PUBLIC_KEY'),
    'STRIPE_SECRET_KEY': os.getenv('STRIPE_SECRET_KEY')
})

bcrypt.init_app(app)
auth.init_app(app)
oidc.init_app(app)

keycloak_openid = KeycloakOpenID(server_url=f"{os.getenv('SERVER_URL')}",
                                 client_id=f"{os.getenv('CLIENT_ID')}",
                                 realm_name=f"{os.getenv('REALM_NAME')}",
                                 client_secret_key=f"{os.getenv('CLIENT_SECRET')}",
                                 verify=True)
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')


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
                        time
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
@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    try:
        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    # Provide the exact Price ID (for example, pr_1234) of the product you want to sell
                    'price': 'price_1MVyz4SAuzkFWObo0IbKqCN3',
                    'quantity': 1,
                },
            ],
            mode='payment',
            success_url="http://localhost:5000" + '/success.html',
            cancel_url="http://localhost:5000" + '/cancel.html',
        )
    except Exception as e:
        return str(e)

    return redirect(checkout_session.url, code=303)


@oidc.accept_token(require_token=True)
@app.route('/add', methods=['POST'])
def addNote():
    query = """
        mutation AddNote($email: String!, $title: String!, $body: String, $time: Time){
            addNote(email: $email, title: $title, body: $body, time: $time){
                note{
                    title
                }
            }
        }
    """
    variables = {
        "email": oidc.user_getinfo(['email']).get('email'),
        "title": request.form.get("title"),
        "body": request.form.get("body"),
        "time": request.form.get("time")
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
                    title
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
        mutation UpdateNote($noteIds: [Int]!, $titles: [String], $bodys: [String], $times: [Time]) {
            updateNote(noteIds: $noteIds, titles: $titles, bodys: $bodys, times: $times) {
                note {
                    title
                    body
                    time
                }
            }
        }
    """
    variables = {
        "noteIds": request.form.getlist("noteid"),
        "titles": request.form.getlist("title"),
        "bodys": request.form.getlist("body"),
        "times": request.form.getlist("time")
    }
    auth_required_schema.execute(query, variables=variables)
    return redirect(url_for('index'))


@app.teardown_appcontext
def shutdown_session(exception=None):
    dbsession.remove()
