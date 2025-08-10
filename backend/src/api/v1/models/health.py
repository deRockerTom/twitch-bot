from pydantic import BaseModel


class HealthAPIResponse(BaseModel):
    status: str
