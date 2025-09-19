from pydantic import BaseModel


class CreateMovieRequest(BaseModel):
    title: str
    plot: str | None = None
