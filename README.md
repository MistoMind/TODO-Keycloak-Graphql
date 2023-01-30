# Internship-Project

## Configuring Keycloak Server
Firstly we will start keycloak server using docker container
```
docker run -p 8080:8080 -e KEYCLOAK_ADMIN=admin -e KEYCLOAK_ADMIN_PASSWORD=admin quay.io/keycloak/keycloak:20.0.3 start-dev
```
- Goto `http://localhost:8080` and login using `username: admin` & `password: admin`.
- Create a new realm named webapp.
- Go to Clients section import client and select `flask_api.json` from the directory.


## Configuring Web Application
- Install `requirements.txt`
```
pip install -r requirements.txt
```
- Create the database
```
python create_db.py
```

- Create a `.env` file containing these variables:
```
SECRET=""
SERVER_URL="http://localhost:8080/"
REALM_NAME="webapp"
CLIENT_ID="flask_api"
CLIENT_SECRET="UVWM60dwzeJrXYh7xvwJnjMVsWx3MLsE"
STRIPE_PUBLIC_KEY=""
STRIPE_SECRET_KEY=""
```
You will get the `STRIPE_PUBLIC_KEY` & `STRIPE_SECRET_KEY` on the  `https://dashboard.stripe.com/test/developers`.

## Running the Web Application
```
python run.py
```
The Webapp will be deployed on `http://localhost:5000/`.
