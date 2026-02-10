from pydantic import BaseModel

class CampaignData(BaseModel):
    username: str
    feedback_date: str
    campaign_id: str
    comment: str

class Credentials(BaseModel):
    email: str
    password : int