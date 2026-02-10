from datetime import datetime, timedelta
import os
from dotenv import load_dotenv, dotenv_values
import jwt

load_dotenv()

SECRET_KEY = os.getenv("API_SECRET")

fake_users_db = {
    "johndoe": {
        "email": os.getenv("API_EMAIL"),
        "password": os.getenv("API_PASSWORD")
    }
}

def create_token(email):
    payload = {
        "sub": email,  # Identifiant de l'utilisateur (doit être une chaîne)
        "exp": datetime.utcnow() + timedelta(hours=1),  # Expiration (1h)
        "iat": datetime.utcnow()  # Date de création
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def decode_token(token): # Décode un token JWT
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise Exception("Token expired")
    except jwt.InvalidTokenError:
        raise Exception("Invalid token")

def auth_user(email, password):
    if (email == os.getenv("API_EMAIL"), password == os.getenv("API_PASSWORD")):
        return {"message":"Login successful"}, 200
    else:
        return {"message": "Invalid credentials"}, 401
