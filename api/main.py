import os
import datetime
from typing import Annotated
from fastapi import FastAPI, HTTPException, Header
from dotenv import load_dotenv, dotenv_values
from pydantic import BaseModel
from utils.utils import create_token, decode_token, auth_user
from utils.models import CampaignData, Credentials, User
from databricks.sdk import WorkspaceClient
from pymongo import MongoClient

load_dotenv() # Loading environmental variables
app = FastAPI() # Creating FastAPI session

client = MongoClient("mongodb://mongo:27017") # Creating connection with MongoDB database
collection = client.raw.events # Creating MongoDB collections
campaign_db = collection["campaign_db"]
log_db = collection["logs_db"]
user_db = collection["user_db"]

dblist = client.raw.list_collection_names()

if "events.user_db" not in dblist:
    master_data = { # Initializing master user
        "_id": os.getenv("API_EMAIL"),
        "password": int(os.getenv("API_PASSWORD")),
        "role": "master"
    }
    user_db.insert_one(master_data)

@app.get("/") # Health check
async def get_health():
    return {"message":"The API endpoint is up."}

@app.post("/afc/signup") # Endpoint for creating users
async def user_signup(user: User):

    user_data = {
        "_id" : user.email,
        "password" : user.password,
        "role" : user.role.value,
    }

    user_db.insert_one(user_data)
    token = create_token(user.email, user.role.value)

    return {"message":"User successfully created!","user": user_data["_id"], "access_token": token}

@app.post("/afc/login_prod") # Endpoint for logging in as a producer
async def post_credentials(credentials: Credentials):
    
    try:
        role = auth_user(credentials.email, credentials.password, "producer")
    except Exception:
        raise HTTPException(401, {"message":"Login failed."})
    token = create_token(credentials.email, role)
    return {"access_token": token}

@app.post("/afc/login_cons") # Endpoint for logging in as a consumer
async def post_credentials(credentials: Credentials):
    
    try:
        role = auth_user(credentials.email, credentials.password, "consumer")
    except Exception:
        raise HTTPException(401, {"message":"Login failed."})
    token = create_token(credentials.email, role)
    return {"access_token": token}

@app.get("/afc/api") # Endpoint for getting all feedback data
async def get_feedback(Authorization: Annotated[str | None, Header()] = None):

    try:
        decoded = decode_token(Authorization, "consumer")
    except Exception:
        return {"message":"Token rejected, either expired or invalid."}

    feedbacks = []
    query_data = campaign_db.find()

    for feedback in query_data:
        feedback.pop('_id', None) 
        feedbacks.append(feedback)

    return{"message" : feedbacks}

@app.post("/afc/api")
async def post_feedback(feedback: CampaignData, Authorization: Annotated[str | None, Header()] = None):

    try:
        decoded = decode_token(Authorization, "producer")
    except Exception:
        return {"message":"Token rejected, either expired, invalid, or not containing the correct role."}
        
    feedback_data = {
        "user" : feedback.username,
        "feedback_date" : feedback.feedback_date,
        "campaign_id" : feedback.campaign_id,
        "comment" : feedback.comment,
        "creation_time": datetime.datetime.now()
    }

    campaign_db.insert_one(feedback_data)

    log_data = {
        "user_email" : decoded.get("sub"),
        "user_role" : decoded.get("roe"),
        "token_expiration" : datetime.datetime.fromtimestamp(decoded.get("exp")),
        "token_creation" : datetime.datetime.fromtimestamp(decoded.get("iat")),
        "operation" : "post",
        "body":feedback_data
    }

    log_db.insert_one(log_data)

    feedback_data.pop('_id', None) 

    return {
    "message": "Feedback registered successfully!",
    "created": feedback_data
    }
    
@app.get("/afc/logs")
async def get_logs(Authorization: Annotated[str | None, Header()] = None):

    try:
        decoded = decode_token(Authorization, "consumer")
    except Exception:
        return {"message":"Token rejected, either expired, invalid, or not containing the correct role."}

    logs = list(log_db.find())

    for log in logs:
        log["_id"] = str(log["_id"])
        log["body"]["_id"] = str(log["body"]["_id"])

    return {"message": logs}

