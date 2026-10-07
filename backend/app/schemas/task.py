from pydantic import BaseModel


class BackgroundTaskResponse(BaseModel):
    accepted: bool
    message: str
