from pydantic import BaseModel


class QueryLlmRequest(BaseModel):
    query: str
