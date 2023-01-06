import graphene
from graphene import relay
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from models import db_session, Todo as TodoModel, User as UserModel
# from models_flask import Todo as TodoModel, User as UserModel

class User(SQLAlchemyObjectType):
    class Meta:
        model = UserModel
        interfaces = (relay.Node, )


class Todo(SQLAlchemyObjectType):
    class Meta:
        model = TodoModel
        interfaces = (relay.Node, )


class Query(graphene.ObjectType):
    node = relay.Node.Field()
    all_users = SQLAlchemyConnectionField(User.connection)
    all_todos = SQLAlchemyConnectionField(Todo.connection)

schema = graphene.Schema(query=Query)
