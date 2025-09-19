from abc import ABC, abstractmethod

from sqlmodel import Session, text

from python_pg_bigm.entity.movie import Movie
from python_pg_bigm.helper.transformer import create_embedding


class MovieRepositoryInterface(ABC):
    @abstractmethod
    def create(self, title: str, plot: str | None) -> Movie:
        pass

    @abstractmethod
    def search(self, q: str, limit: int = 5) -> list[Movie]:
        pass


class MovieRepository(MovieRepositoryInterface):
    def __init__(self, session: Session):
        self.session = session

    def create(self, title: str, plot: str | None = None, embedding: list[float] | None = None) -> Movie:
        movie = Movie(title=title, plot=plot, embedding=embedding)
        self.session.add(movie)
        self.session.commit()
        self.session.refresh(movie)
        return movie

    def search(self, q: str, limit: int = 5) -> list[Movie]:
        q_embedding = create_embedding(q)

        sql = text(
            """
            WITH semantic_search AS (SELECT m.id,
                                            m.title,
                                            m.plot,
                                            1 - (m.embedding <=> :q_embedding) AS vector_similarity
                                     FROM public.movies m
                                     ORDER BY vector_similarity DESC
                LIMIT 20
                )
               , full_text_search AS (
            SELECT m.id, m.title, m.plot, similarity(m.title, :q) AS trigram_similarity
            FROM public.movies m
            WHERE m.title =% :q
                )
            SELECT m.id,
                   m.title,
                   m.plot,
                   (COALESCE(ss.vector_similarity, 0) * 0.7) + (COALESCE(fts.trigram_similarity, 0) * 0.3) AS score
            FROM public.movies m
                     LEFT JOIN semantic_search ss ON m.id = ss.id
                     LEFT JOIN full_text_search fts ON m.id = fts.id
            WHERE ss.id IS NOT NULL
               OR fts.id IS NOT NULL
            ORDER BY score DESC LIMIT :limit;
            """
        )

        rows = self.session.exec(sql.bindparams(q=q, q_embedding=str(q_embedding), limit=limit)).all()
        return [Movie(**row._mapping) for row in rows]
