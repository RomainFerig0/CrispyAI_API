import os
import datetime
from typing import Annotated
from fastapi import FastAPI, HTTPException, Header
from dotenv import load_dotenv, dotenv_values
from pydantic import BaseModel
from utils.utils import create_token, decode_token, auth_user
from utils.models import CampaignData, Credentials
from databricks.sdk import WorkspaceClient
from pymongo import MongoClient

load_dotenv()
app = FastAPI()

'''wc = WorkspaceClient(
    host=os.getenv("DATABRICKS_HOST"),
    client_id=os.getenv("DATABRICKS_CLIENT_ID"),
    client_secret=os.getenv("DATABRICKS_CLIENT_SECRET")
)

headers = wc.config.authenticate()
'''

client = MongoClient("mongodb://localhost:27017")
collection = client.raw.events
campaign_db = collection["campaign_db"]
log_db = collection["logs_db"]

@app.post("/login")
async def login_for_access_token(credentials: Credentials):

    message, code = auth_user(credentials.email, credentials.password)
    if code == 401:
        raise HTTPException(status_code=code, detail=message)
    elif code == 200:
        token = create_token(credentials.email)
        return {"access_token": token}

@app.get("/afc/api")
async def get_api(Authorization: Annotated[str | None, Header()] = None):

    try:
        decoded = decode_token(Authorization)
    except Exception:
        return {"message":"Token rejected, either expired or invalid."}

    feedbacks = []
    query_data = campaign_db.find({ "feedback_date" : "2025-01-01" })

    for feedback in query_data:
        feedback["_id"] = str(feedback["_id"])
        feedbacks.append(feedback)

    return{"message" : feedbacks}

@app.post("/afc/api")
async def post_api(feedback: CampaignData, Authorization: Annotated[str | None, Header()] = None):

    try:
        decoded = decode_token(Authorization)
    except Exception:
        return {"message":"Token rejected, either expired or invalid."}
        
    feedback_data = {
        "user" : feedback.username,
        "feedback_date" : feedback.feedback_date,
        "campaign_id" : feedback.campaign_id,
        "comment" : feedback.comment
    }

    log_data = {
        "user_email" : decoded.get("sub"),
        "token_expiration" : datetime.datetime.fromtimestamp(decoded.get("exp")),
        "token_creation" : datetime.datetime.fromtimestamp(decoded.get("iat")),
        "connection_time": datetime.datetime.now(),
        "operation" : "post",
        "endpoint" : "/afc/api"
    }

    print(feedback_data)
    print(log_data)

    print('gonna insert')
    campaign_db.insert_one(feedback_data)
    log_db.insert_one(log_data)
    print('have inserted')

    feedback_data.pop('_id', None) 

    return {
    "message": "Feedback registered successfully!",
    "feedback": feedback_data
    }
    
@app.get("/afc/logs")
async def get_all_logs(Authorization: Annotated[str | None, Header()] = None):

    try:
        decoded = decode_token(Authorization)
    except Exception:
        return {"message":"Token rejected, either expired or invalid."}

    logs = []
    query_data = log_db.find({ "operation" : "post" })

    for log in query_data:
        log["_id"] = str(log["_id"])
        logs.append(log)

    return{"message" : logs}

def main():

    dblist = client.list_database_names()

    if "campaign_db" in dblist:
        print(f"The database 'campaign_db' exists.")
    else:
        print(f"The database 'campaign_db' does not exist")

main()

