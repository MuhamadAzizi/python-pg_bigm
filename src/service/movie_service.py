from src.model.api_response import ApiResponse, ApiErrorResponse, ApiSuccessResponse
from src.repository.movie_repository import MovieRepository
from abc import ABC, abstractmethod


class MovieServiceInterface(ABC):
    @abstractmethod
    def search(self, q: str, limit: int = 5) -> ApiResponse:
        pass


class MovieService(MovieServiceInterface):
    def __init__(self, movie_repository: MovieRepository):
        self.movie_repository = movie_repository

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
