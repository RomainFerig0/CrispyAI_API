"""
Utility functions called by the API
JWT create and encode functions
User authentication function
"""

from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import jwt
from pymongo import MongoClient
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

load_dotenv() # Loading environmental variables
if os.getenv("MODE") not in ["local", "container"]:
    raise ValueError("Illegal execution parameter")

api_mode = os.getenv("MODE")
if api_mode == "container":
    client = MongoClient("mongodb://mongo:27017") # Creating connection with MongoDB database
else:
    client = MongoClient("mongodb://localhost:27017")

collection = client.raw.events
user_db = collection["user_db"]

SECRET_KEY = os.getenv("API_SECRET")

def create_token(email, role): # Generates a JWT token conaining the identifier and role of the user
    payload = {
        "sub": email,
        "roe": role, 
        "exp": datetime.utcnow() + timedelta(hours=1),  # Expiration date (1h)
        "iat": datetime.utcnow() 
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def decode_token(token, role): # Decodes a JWT token and assesses its validity
    try:  
        decoded = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        if decoded.get("roe") not in [role, 'master']:  # Compares JWT-embedded role with required authorization
             raise Exception("Invalid role")
        return decoded
    except jwt.ExpiredSignatureError:
        raise Exception("Token expired")
    except jwt.InvalidTokenError:
        raise Exception("Invalid token")
    except ValueError:
        raise Exception("Malformed token")

def auth_user(email, password, role): # Verifies if a user exist and has the correct role

    query_data = user_db.find_one({"_id":email}, {"password":1, "role":1})

    if not query_data or not pwd_context.verify(password, query_data["password"]):
        raise Exception("Incorrect credentials.")
    elif (query_data['role'] not in [role, 'master']):
        raise Exception("You do not have the rights to access this endpoint.")
    
    return query_data['role']

