from fastapi import APIRouter, UploadFile, File, Depends

from python_pg_bigm.model.query_llm_request import QueryLlmRequest
from python_pg_bigm.service.llm_service import LlmService

router = APIRouter(prefix="/llm", tags=["LLM"])

def get_llm_service() -> LlmService:
    return LlmService()

@router.post("/upload")
def upload(file: UploadFile = File(...), llm_service: LlmService = Depends(get_llm_service)):
    return llm_service.upload(file)


@router.post("/query")
def query(request: QueryLlmRequest, llm_service: LlmService = Depends(get_llm_service)):
    return llm_service.query(request)
