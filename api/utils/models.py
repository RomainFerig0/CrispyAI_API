from pydantic import BaseModel
from enum import Enum

class Roles(Enum):
    afc = 'producer'
    databricks = 'consumer'

class CampaignData(BaseModel):
    username: str
    feedback_date: str
    campaign_id: str
    comment: str

class Credentials(BaseModel):
    email: str
    password: int

class User(BaseModel):
    email: str
    password: int
    role: Roles
