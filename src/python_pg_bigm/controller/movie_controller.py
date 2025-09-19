from fastapi import APIRouter, Depends
from sqlmodel import Session

from python_pg_bigm.config.database import get_session
from python_pg_bigm.model.create_movie_request import CreateMovieRequest
from python_pg_bigm.repository.movie_repository import MovieRepository
from python_pg_bigm.service.movie_service import MovieService

router = APIRouter(prefix="/movie", tags=["Movie"])


def get_movie_service(session: Session = Depends(get_session)) -> MovieService:
    movie_repository = MovieRepository(session)
    return MovieService(movie_repository)


@router.post("/")
async def create(
        data: CreateMovieRequest,
        movie_service: MovieService = Depends(get_movie_service),
):
    return movie_service.create(data.title, data.plot)


@router.get("/search")
async def search(
        q: str,
        limit: int = 5,
        movie_service: MovieService = Depends(get_movie_service)
):
    return movie_service.search(q, limit)
