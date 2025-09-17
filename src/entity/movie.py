from sqlalchemy.types import UserDefinedType
from sqlmodel import SQLModel, Field, Column, Index


class Vector(UserDefinedType):
    def __init__(self, dimensions: int):
        self.dimensions = dimensions

    def get_col_spec(self, **kwargs):
        return f"VECTOR({self.dimensions})"

    def bind_expression(self, bindvalue):
        return bindvalue

    def column_expression(self, col):
        return col


class Movie(SQLModel, table=True):
    __tablename__ = "movies"

    id: int | None = Field(default=None, primary_key=True)
    title: str = Field(nullable=False)
    plot: str | None = Field(default=None)
    embedding: list[float] | None = Field(sa_column=Column(Vector(384)))

    __table_args__ = (
        Index(
            "idx_movies_title_gin",
            "title",
            postgresql_using="gin",
            postgresql_ops={"title": "gin_trgm_ops"},
        ),
        Index(
            "idx_movies_embedding_ivf",
            "embedding",
            postgresql_using="ivfflat",
            postgresql_ops={"embedding": "vector_cosine_ops"},
            postgresql_with={"lists": 100}
        )
    )
