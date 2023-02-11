from pydantic import BaseModel, HttpUrl


class LoggerWarning(BaseModel):
    status: str
    short_status: str
    url: HttpUrl
