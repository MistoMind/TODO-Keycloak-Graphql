from flask_bcrypt import Bcrypt
from flask_graphql_auth import GraphQLAuth
from flask_oidc import OpenIDConnect

bcrypt = Bcrypt()
auth = GraphQLAuth()
oidc = OpenIDConnect()
