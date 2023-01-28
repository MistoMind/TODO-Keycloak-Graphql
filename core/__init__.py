from flask import Flask, request, jsonify, render_template, redirect, url_for
from flask_graphql import GraphQLView
from extensions import bcrypt, auth, jwt
from schema import auth_required_schema, schema
from dotenv import load_dotenv
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    get_jwt_identity,
    jwt_required
)
import os
from models import User, session

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('secret')
app.config['JWT_SECRET_KEY'] = os.getenv('jwtsecret')

bcrypt.init_app(app)
auth.init_app(app)
jwt.init_app(app)
curr_email = "khush@gmail.com"


def currUser():
    return session.query(User).filter_by(email=curr_email).first()


@app.route('/')
def index():
    return render_template("index.html", user=currUser())


@app.route('/login', methods=['POST'])
def login():
    data = request.get_json(force=True)
    user = session.query(User).filter_by(email=data['email']).first()
    if not user:
        return {
            "ok": True,
            "message": "User with email not found"
        }, 404
    if bcrypt.check_password_hash(user.password, data['password']):
        token = create_access_token(identity=data['email'])
        return jsonify(access_token=token), 200
    return {
        "ok": True,
        "message": "Incorrect password"
    }, 401


@app.route('/add', methods=['POST'])
@jwt_required()
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
        "email": curr_email,
        "title": request.form.get("title"),
        "body": request.form.get("body")
    }
    auth_required_schema.execute(query, variables=variables)
    return redirect(url_for('index'))


@app.route('/delete', methods=['POST'])
@jwt_required()
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


@app.route('/update', methods=['POST'])
@jwt_required()
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


def graphql():
    view = GraphQLView.as_view(
        'graphql',
        schema=auth_required_schema,
        graphiql=True,
        get_context=lambda: {
            'session': session,
            'request': request,
            'uid': get_jwt_identity()
        }
    )
    return jwt_required(view)


app.add_url_rule(
    '/api',
    view_func=graphql()
)

app.add_url_rule(
    '/api',
    view_func=GraphQLView.as_view(
        'api',
        schema=schema,
        graphiql=True
    )
)
