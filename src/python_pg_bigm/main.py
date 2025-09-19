import uvicorn
from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from python_pg_bigm.config.database import init_db
from python_pg_bigm.controller import movie_controller
from python_pg_bigm.model.api_response import ApiErrorResponse

app = FastAPI()


@app.on_event("startup")
def on_startup():
    init_db()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    print(request.query_params)

    body = ApiErrorResponse(
        status=False,
        message="Validation error",
        errors=exc.errors(),
    )

    return JSONResponse(
        status_code=400,
        content=jsonable_encoder(body),
    )


app.include_router(movie_controller.router)

if __name__ == "__main__":
    uvicorn.run("main:app")
