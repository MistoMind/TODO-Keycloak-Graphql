import graphene
from graphene_sqlalchemy import SQLAlchemyObjectType
from models import session, User as UserModel, Notes as NotesModel
from extensions import bcrypt
from typing import Optional


class User(SQLAlchemyObjectType):
    class Meta:
        model = UserModel


class Notes(SQLAlchemyObjectType):
    class Meta:
        model = NotesModel


class GetUser(graphene.Mutation):
    class Arguments:
        email = graphene.String()

    ok = graphene.Boolean()
    user = graphene.Field(User)

    def mutate(self, root, email):
        user = session.query(UserModel).filter_by(email=email).first()
        ok = True
        return GetUser(ok=ok, user=user)


class CreateUser(graphene.Mutation):
    class Arguments:
        name = graphene.String()
        email = graphene.String()
        password = graphene.String()

    ok = graphene.Boolean()
    user = graphene.Field(User)

    def mutate(self, root, name, email, password):
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
        return CreateUser(ok=ok, user=new_user)


class NoAuthMutation(graphene.ObjectType):
    createUser = CreateUser.Field()


class AddNote(graphene.Mutation):
    class Arguments:
        email = graphene.String()
        title = graphene.String()
        body = graphene.String()
        time = graphene.Time()

    ok = graphene.Boolean()
    note = graphene.Field(Notes)

    def mutate(self, root, email, title, body, time):
        user = session.query(UserModel).filter_by(email=email).first()
        new_note = NotesModel(
            title=title,
            body=body,
            time=time,
            user=user
        )
        session.add(new_note)
        session.commit()
        ok = True
        return AddNote(ok=ok, note=new_note)


class UpdateNote(graphene.Mutation):
    class Arguments:
        note_ids = graphene.List(graphene.Int)
        titles = graphene.List(graphene.String)
        bodys = graphene.List(graphene.String)
        times = graphene.List(graphene.Time)

    ok = graphene.Boolean()
    note = graphene.Field(Notes)

    def mutate(self, root, note_ids, titles, bodys, times):
        for i in range(0, len(note_ids)):
            note = session.query(NotesModel).filter_by(id=note_ids[i]).first()
            print(note.title)
            print(note.body)
            print(note.time)
            note.title = titles[i]
            note.body = bodys[i]
            note.time = times[i]
        session.commit()
        ok = True
        note = note
        return UpdateNote(ok=ok, note=note)


class DeleteNote(graphene.Mutation):
    class Arguments:
        note_ids = graphene.List(graphene.Int)

    ok = graphene.Boolean()
    note = graphene.Field(Notes)

    def mutate(self, root, note_ids):
        print(note_ids)
        for noteid in note_ids:
            note = session.query(NotesModel).filter_by(id=noteid).first()
            session.delete(note)
        session.commit()
        ok = True
        note = note
        return DeleteNote(ok=ok, note=note)


class AuthMutation(graphene.ObjectType):
    getUser = GetUser.Field()
    addNote = AddNote.Field()
    updateNote = UpdateNote.Field()
    deleteNote = DeleteNote.Field()


class Query(graphene.ObjectType):
    allNotes = graphene.List(Notes, email=graphene.String())

    def resolve_allNotes(self, root, email):
        user = session.query(UserModel).filter_by(email=email).first()
        return user.notes


auth_required_schema = graphene.Schema(query=Query, mutation=AuthMutation)
schema = graphene.Schema(mutation=NoAuthMutation)
