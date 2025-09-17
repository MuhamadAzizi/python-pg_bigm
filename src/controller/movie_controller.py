from pydantic import ValidationError

from src.config.database import get_session
from src.model.api_response import ApiResponse
from src.repository.movie_repository import MovieRepository
from src.service.movie_service import MovieService
from fastapi import APIRouter, Depends
from sqlmodel import Session

router = APIRouter(prefix="/movie", tags=["Movie"])


def get_movie_service(session: Session = Depends(get_session)) -> MovieService:
    movie_repository = MovieRepository(session)
    return MovieService(movie_repository)

@router.get("/search")
async def search(
        q: str,
        limit: int = 5,
        movie_service: MovieService = Depends(get_movie_service)
):
    return movie_service.search(q, limit)