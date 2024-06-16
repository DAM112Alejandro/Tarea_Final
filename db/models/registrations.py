from pydantic import BaseModel

class Registrations(BaseModel):
    id_Event: str
    id_User: str