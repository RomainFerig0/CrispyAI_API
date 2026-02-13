"""
Main file of the program
Defines all API endpoints and associated operations/functions
"""

import os
import datetime
from typing import Annotated
from fastapi import FastAPI, HTTPException, Header
from dotenv import load_dotenv
from utils.utils import create_token, decode_token, auth_user
from models.models import Credentials, FeedbackRequest, FeedbackRequest
from pymongo import MongoClient
import pymongo
import dateutil.parser
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

load_dotenv() # Loading environmental variables
if os.getenv("MODE") not in ["local", "container"]:
    raise ValueError("Illegal execution parameter")

app = FastAPI() # Creating FastAPI session

if os.getenv("MODE") == "container":
    client = MongoClient("mongodb://mongo:27017") # Creating connection with MongoDB database
else:
    client = MongoClient("mongodb://localhost:27017")

collection = client.raw.events # Creating MongoDB collections
campaign_db = collection["campaign_db"]
log_db = collection["log_db"]
user_db = collection["user_db"]

dblist = client.raw.list_collection_names()

if "events.user_db" not in dblist:

    predefined_users = [
    {"_id" : os.getenv("API_EMAIL"), "password": pwd_context.hash(os.getenv("API_PASSWORD")), "role":"master"},
    {"_id" : os.getenv("API_CONS_EMAIL"), "password":pwd_context.hash(os.getenv("API_CONS_PASSWORD")), "role":"consumer"},
    {"_id" : os.getenv("API_PROD_EMAIL"), "password":pwd_context.hash(os.getenv("API_PROD_PASSWORD")), "role":"producer"}
    ]

    user_db.insert_many(predefined_users)

@app.get("/", status_code=200) # Health check
async def get_health():
    return {"message":"The API endpoint is up."}

@app.post("/afc/login/{role}", status_code=201) # Authenticates a user and grants a JWT
async def post_credentials(role: str, credentials: Credentials):
    
    try:
        role_user = auth_user(credentials.email, credentials.password, role)
    except Exception:
        raise HTTPException(401, {"message":"Login failed, access unauthorized."})
    token = create_token(credentials.email, role_user)
    return {"access_token": token}

@app.post("/afc/api", status_code=201)
async def post_feedback(feedback: FeedbackRequest, Authorization: Annotated[str | None, Header()] = None):

    try:
        decoded = decode_token(Authorization, "producer")
    except Exception:
    
        log_data = {
            "user_email" : decoded.get("sub"),
            "user_role" : decoded.get("roe"),
            "token_expiration" : datetime.datetime.fromtimestamp(decoded.get("exp")),
            "token_creation" : datetime.datetime.fromtimestamp(decoded.get("iat")),
            "operation" : "post",
            "status": "refused"
        }

        log_db.insert_one(log_data)

        raise HTTPException(401, {"message":"Token rejected, either expired, invalid, or not containing the correct role."})
    
    feedbacks = feedback.root if isinstance(feedback.root, list) else [feedback.root]    # Handle both single object and list
    created_feedbacks = []
    
    for single_feedback in feedbacks:
        feedback_data = {
            "user" : single_feedback.username,
            "feedback_date" : single_feedback.feedback_date,
            "campaign_id" : single_feedback.campaign_id,
            "comment" : single_feedback.comment,
            "creation_time": datetime.datetime.now()
        }

        campaign_db.insert_one(feedback_data)

        log_data = {
            "user_email" : decoded.get("sub"),
            "user_role" : decoded.get("roe"),
            "token_expiration" : datetime.datetime.fromtimestamp(decoded.get("exp")),
            "token_creation" : datetime.datetime.fromtimestamp(decoded.get("iat")),
            "operation" : "post",
            "feedback_id":str(feedback_data["_id"]),
            "creation_time": feedback_data["creation_time"],
            "status": "accepted"
        }

        log_db.insert_one(log_data)

        feedback_data.pop('_id', None)
        created_feedbacks.append(feedback_data)

    return {
        "message": "Feedback registered successfully!",
        "created": created_feedbacks if len(created_feedbacks) > 1 else created_feedbacks[0]
    }

@app.get("/afc/api", status_code=200) # Endpoint for getting all feedback data
async def get_feedback(Authorization: Annotated[str | None, Header()] = None):

    try:
        decode_token(Authorization, "consumer")
    except Exception:
        return {"message":"Token rejected, either expired or invalid."}

    feedbacks = []
    query_data = campaign_db.find().sort(("creation_time"))

    for feedback_data in query_data:
        feedback_data.pop('_id', None) 
        feedbacks.append(feedback_data)

    return{"message" : feedbacks}

@app.get("/afc/api/{watermark}", status_code=200) # Endpoint for getting all feedback data
async def get_feedback(watermark : str, Authorization: Annotated[str | None, Header()] = None):

    try:
        decode_token(Authorization, "consumer")
    except Exception:
        return {"message":"Token rejected, either expired or invalid."}

    feedbacks = []
    query_data = campaign_db.find({"creation_time":{"$gt":dateutil.parser.parse(watermark)}})

    for feedback_data in query_data:
        feedback_data.pop('_id', None)
        feedbacks.append(feedback_data)

    return{"message" : feedbacks}
    
@app.get("/afc/logs", status_code=200) # Get all logs, ordered by time
async def get_logs(Authorization: Annotated[str | None, Header()] = None):

    try:
        decoded = decode_token(Authorization, "consumer")
    except Exception:
        return {"message":"Token rejected, either expired, invalid, or not containing the correct role."}

    logs = list(log_db.find().sort(("creation_time")))

    for log in logs:
        log["_id"] = str(log["_id"])

    return {"message": logs}