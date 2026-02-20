"""
Main file of the program
Defines all API endpoints and associated operations/functions
"""

import os
import datetime
from typing import Annotated
from fastapi import FastAPI, Header
from fastapi.responses import JSONResponse
from dotenv import load_dotenv
from utils.utils import create_token, decode_token, auth_user
from models.models import Credentials, FeedbackRequest
from pymongo import MongoClient
import pymongo
import dateutil.parser
from passlib.context import CryptContext
import requests

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
api_mode = os.getenv("MODE")

load_dotenv() # Loading environmental variables
if api_mode not in ["local", "container"]:
    raise ValueError("Illegal execution parameter")

app = FastAPI() # Initializing FastAPI session

if os.getenv("MODE") == "container": # Initializing connection with MongoDB database
    client = MongoClient("mongodb://mongo:27017")
else:
    client = MongoClient("mongodb://localhost:27017")

collection = client.raw.events # Creating MongoDB collections
campaign_db = collection["campaign_db"]
log_db = collection["log_db"]
user_db = collection["user_db"]

dblist = client.raw.list_collection_names()

if "events.user_db" not in dblist: # Inserting 3 primary roles in the database. WARNING :

    predefined_users = [
    {"_id" : os.getenv("API_EMAIL"), "password": pwd_context.hash(str(os.getenv("API_PASSWORD"))), "role":"master"}, # "master" role can use any endpoint.
    {"_id" : os.getenv("API_CONS_EMAIL"), "password":pwd_context.hash(str(os.getenv("API_CONS_PASSWORD"))), "role":"consumer"}, # "consumer" role can only use "get" operations on endpoints.
    {"_id" : os.getenv("API_PROD_EMAIL"), "password":pwd_context.hash(str(os.getenv("API_PROD_PASSWORD"))), "role":"producer"} # "producer" role can only use "post" operations on endpoints.
    ]

    user_db.insert_many(predefined_users)

@app.get("/", status_code=200) # Health check
async def get_health():
    return {"message":"The API endpoint is up."}

@app.post("/afc/login/{role}", status_code=201) # Authenticates a user and grants a JWT
async def post_credentials(role: str, credentials: Credentials):
    
    try:
        role_user = auth_user(credentials.email, credentials.password, role)
    except Exception as e:
        return JSONResponse(
        status_code=401,
        content={"message": e.args},
        )
    
    token = create_token(credentials.email, role_user)
    return {"access_token": token}

@app.post("/afc/api", status_code=201) # Inserts one (or multiple) new feedback into the database and logs the activity
async def post_feedback(feedback: FeedbackRequest, Authorization: Annotated[str | None, Header()] = None):

    try:
        decoded = decode_token(Authorization, "producer") # Accessible only to "producer" and "master"
    except Exception as e:
    
        log_data = {
            "user_email" : decoded.get("sub"),
            "user_role" : decoded.get("roe"),
            "token_expiration" : datetime.datetime.fromtimestamp(decoded.get("exp")),
            "token_creation" : datetime.datetime.fromtimestamp(decoded.get("iat")),
            "operation" : "post",
            "status": "refused",
            "error": e.args
        }

        log_db.insert_one(log_data)

        return JSONResponse(
            status_code=401,
            content={"message": e.args},
        )
    
    feedbacks = feedback.root if isinstance(feedback.root, list) else [feedback.root] # Handles feedback coming as a list or a single JSON object
    created_feedbacks = []
    
    for single_feedback in feedbacks: # Generates a log for every new feedback inserted into the database
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
            "endpoint" : "/afc/api",
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

@app.get("/afc/api", status_code=200) # Fetches all feedback data (full load)
async def get_all_feedback(Authorization: Annotated[str | None, Header()] = None):

    try:
        decoded = decode_token(Authorization, "consumer") # Accessible only to "consumer" and "master"
    except Exception as e:
        return JSONResponse(
            status_code=401,
            content={"message": e.args},
        )
    
    feedbacks = []
    query_data = campaign_db.find().sort("creation_time", -1)

    log_data = {
        "user_email" : decoded.get("sub"),
        "user_role" : decoded.get("roe"),
        "token_expiration" : datetime.datetime.fromtimestamp(decoded.get("exp")),
        "token_creation" : datetime.datetime.fromtimestamp(decoded.get("iat")),
        "operation" : "get",
        "endpoint" : "/afc/api",
        "status": "accepted"
    }

    log_db.insert_one(log_data)

    if not query_data:
        return{"message":"No results found."}
    else:
        for feedback_data in query_data:
            feedback_data.pop('_id', None) 
            feedbacks.append(feedback_data)
        return{"results" : feedbacks}

@app.get("/afc/api/{watermark}", status_code=200) # Fetches all data created after a timestamp (incremental load)
async def get_latest_feedback(watermark : str, Authorization: Annotated[str | None, Header()] = None):

    try:
        decoded = decode_token(Authorization, "consumer")  # Accessible only to "consumer" and "master"
    except Exception as e:
        return JSONResponse(
            status_code=401,
            content={"message": e.args},
        )
    
    feedbacks = []
    query_data = campaign_db.find({"creation_time":{"$gt":dateutil.parser.parse(watermark)}})

    log_data = {
        "user_email" : decoded.get("sub"),
        "user_role" : decoded.get("roe"),
        "token_expiration" : datetime.datetime.fromtimestamp(decoded.get("exp")),
        "token_creation" : datetime.datetime.fromtimestamp(decoded.get("iat")),
        "operation" : "get",
        "endpoint" : f"/afc/api/{watermark}",
        "status": "accepted"
    }

    log_db.insert_one(log_data)

    if not query_data:
        return{"message":"No results found."}
    else:
        for feedback_data in query_data:
            feedback_data.pop('_id', None) 
            feedbacks.append(feedback_data)
        return{"results" : feedbacks}
    
@app.get("/afc/logs", status_code=200) # Fetches all logs, ordered by time
async def get_logs(Authorization: Annotated[str | None, Header()] = None):

    try:
        decode_token(Authorization, "consumer")  # Accessible only to "consumer" and "master"
    except Exception as e:
        return JSONResponse(
            status_code=401,
            content={"message": e.args},
        )
    
    logs = list(log_db.find().sort("creation_time", -1))

    for log in logs:
        log["_id"] = str(log["_id"])

    return {"message": logs}