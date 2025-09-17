from abc import ABC, abstractmethod

from src.helper.transformer import create_embedding
from src.model.api_response import ApiResponse, ApiSuccessResponse
from src.repository.movie_repository import MovieRepository


class MovieServiceInterface(ABC):
    @abstractmethod
    def create(self, title: str, plot: str | None) -> ApiResponse:
        pass

    @abstractmethod
    def search(self, q: str, limit: int = 5) -> ApiResponse:
        pass


class MovieService(MovieServiceInterface):
    def __init__(self, movie_repository: MovieRepository):
        self.movie_repository = movie_repository

    def create(self, title: str, plot: str | None = None) -> ApiResponse:
        embedding = None
        if plot is not None:
            embedding = create_embedding(plot)

        row = self.movie_repository.create(title, plot, embedding)
        return ApiSuccessResponse(
            status=True,
            message="Success create data",
            data={
                "id": row.id
            }
        )

    def search(self, q: str, limit: int = 5) -> ApiResponse:
        meta = {"q": q, "limit": limit}
        rows = self.movie_repository.search(q, limit)

        if not rows:
            return ApiSuccessResponse(
                status=True,
                message="No data available",
                data=[],
                meta=meta
            )

        return ApiSuccessResponse(
            status=True,
            message="Success get data",
            data=rows,
            meta=meta
        )
