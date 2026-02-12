from datetime import datetime, timedelta
from fastapi import HTTPException
import os
from dotenv import load_dotenv, dotenv_values
import jwt
from pymongo import MongoClient

load_dotenv()

if os.getenv("MODE") == "container":
    client = MongoClient("mongodb://mongo:27017") # Creating connection with MongoDB database
else:
    client = MongoClient("mongodb://localhost:27017")

collection = client.raw.events
campaign_db = collection["campaign_db"]
log_db = collection["logs_db"]
user_db = collection["user_db"]

SECRET_KEY = os.getenv("API_SECRET")

def create_token(email, role):
    payload = {
        "sub": email,  # Identifiant de l'utilisateur (doit être une chaîne)
        "roe": role, # Rôle de l'utilisateur
        "exp": datetime.utcnow() + timedelta(hours=1),  # Expiration (1h)
        "iat": datetime.utcnow()  # Date de création
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def decode_token(token, role): # Décode un token JWT
    try:  
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        if decoded.get("roe") not in [role, 'master']:
             raise Exception("Invalid role")
        return decoded
    except jwt.ExpiredSignatureError:
        raise Exception("Token expired")
    except jwt.InvalidTokenError:
        raise Exception("Invalid token")

def auth_user(email, password, role):

    query_data = user_db.find_one({"_id":email}, {"password":1, "role":1})

    if (not query_data or int(query_data["password"]) != password):
        raise HTTPException(401, {"message":"Incorrect credentials."})
    elif (query_data['role'] not in [role, 'master']):
        raise HTTPException(401, {"message": "You do not have the rights to access this endpoint."})
    return query_data['role'] # Retourne le rôle de l'utilisateur pour construire le JWT


