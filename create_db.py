from models import Base, User, session

Base.metadata.create_all()

# Currently User can be added using this file but in later commit's I'll be making user creation with Keycloak User Register.

user = User()
user.name = "Example Name"
user.email = "example@mail-server.com"
user.password = "example-password"
user.premium = False
session.add(user)
session.commit()
