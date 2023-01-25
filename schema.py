import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType, SQLAlchemyConnectionField
from models import session, User as UserModel, Notes as NotesModel
from extensions import bcrypt
from typing import Optional

class User(SQLAlchemyObjectType):
    class Meta:
        model = UserModel


class Notes(SQLAlchemyObjectType):
    class Meta:
        model = NotesModel


class createUser(graphene.Mutation):
    class Arguments:
        name = graphene.String()
        email = graphene.String()
        password = graphene.String()

    ok = graphene.Boolean()
    user = graphene.Field(User)

    def mutate(self, root, info, name, email, password):
        new_user = UserModel(
            name=name,
            email=email,
            password=str(
                bcrypt.generate_password_hash(password),
                'utf-8'
            )
        )
        session.add(new_user)
        session.commit()
        ok = True
        return createUser(ok=ok, user=new_user)


class addNote(graphene.Mutation):
    class Arguments:
        title = graphene.String()
        body = graphene.String()

    ok = graphene.Boolean
    note = graphene.Field(Notes)

    def mutate(self, root, info, title, body):
        uid = info.context['uid']
        user = session.query(UserModel).filter_by(email=uid).first()
        new_note = NotesModel(
            title=title,
            body=body,
            user=user
        )
        session.add(new_note)
        session.commit()
        ok = True
        return addNote(ok=ok, note=new_note)


class updateNote(graphene.Mutation):
    class Arguments:
        note_id = graphene.Int()
        title = graphene.String()
        body = graphene.String()

    ok = graphene.Boolean
    note = graphene.Field(Notes)

    def mutate(self, root, info, note_id, title: Optional[str]=None, body: Optional[str]=None):
        note = session.query(NotesModel).filter_by(id=note_id).first()
        if not title:
            note.body = body
        elif not body:
            note.title = title
        else:
            note.title = title
            note.body = body
        session.commit()
        ok = True
        note = note
        return updateNote(ok=ok, note=note)


class deleteNote(graphene.Mutation):
    class Arguments:
        id = graphene.Int()

    ok = graphene.Boolean
    note = graphene.Field(Notes)

    def mutate(self, root, info, id):
        note = session.query(NotesModel).filter_by(id=id).first()
        session.delete(note)
        session.commit()
        ok = True
        note = note
        return deleteNote(ok=ok, note=note)


class PostAuthMutation(graphene.ObjectType):
    addNote = addNote.Field()
    updateNote = updateNote.Field()
    deleteNote = deleteNote.Field()


class PreAuthMutation(graphene.ObjectType):
    createUser = createUser.Field()


class Query(graphene.ObjectType):
    findNote = graphene.Field(Notes, id=graphene.Int())
    user_notes = graphene.List(Notes)

    def resolve_user_notes(self, root, info):
        uid = info.context['uid']
        user = session.query(UserModel).filter_by(id=uid).first()
        return user.notes

    def resolve_findNote(self, root, info, id):
        return session.query(UserModel).filter_by(id=id).first()


class PreAuthQuery(graphene.ObjectType):
    all_users = graphene.List(User)

    def resolve_all_users(self, root, info):
        return session.query(UserModel).all()


auth_required_schema = graphene.Schema(query=Query, mutation=PostAuthMutation)
schema = graphene.Schema(query=PreAuthQuery, mutation=PreAuthMutation)
