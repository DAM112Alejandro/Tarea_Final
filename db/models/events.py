import datetime
from pydantic import BaseModel

class Events(BaseModel):
    title: str
    description: str
    start_time: datetime
    location : str
    max_attendees: int
    
    class Config:
        arbitrary_types_allowed = True