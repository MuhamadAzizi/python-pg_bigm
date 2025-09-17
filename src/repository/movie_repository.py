from abc import ABC, abstractmethod
from src.entity.movie import Movie
from sqlmodel import Session, select, text


class MovieRepositoryInterface(ABC):
    @abstractmethod
    def search(self, q: str, limit: int = 5) -> list[Movie]:
        pass


class MovieRepository(MovieRepositoryInterface):
    def __init__(self, session: Session):
        self.session = session

    def search(self, q: str, limit: int = 5) -> list[Movie]:
        sql = text(
            """
            SELECT *
            FROM public.movies m
            WHERE m.title =% :q
            """
        )

        rows = self.session.exec(sql.bindparams(q=q)).all()
        return [Movie(**row._mapping) for row in rows]
