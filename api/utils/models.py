from pydantic import BaseModel, RootModel
from typing import Union, List
from enum import Enum

'''class Roles(Enum):
    producer = 'producer'
    consumer = 'consumer'

class User(BaseModel):
    email: str
    password: int
    role: Roles
'''

class CampaignData(BaseModel):
    username: str
    feedback_date: str
    campaign_id: str
    comment: str

class FeedbackRequest(RootModel[Union[CampaignData, List[CampaignData]]]):
    pass

class Credentials(BaseModel):
    email: str
    password: int
