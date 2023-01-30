from models import Base, User, session

Base.metadata.create_all()
user = User()
user.name = "Khush Seervi"
user.email = "khush@gmail.com"
user.password = "12345678"
user.premium = True
session.add(user)
session.commit()
