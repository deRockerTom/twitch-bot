from pydantic import BaseModel


class DefaultAPIResponse(BaseModel):
    message: str
