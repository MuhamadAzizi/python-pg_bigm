import os.path
import shutil
from abc import ABC, abstractmethod

from fastapi import UploadFile, File, HTTPException
from langchain_community.chat_models import ChatOllama
from langchain_community.document_loaders import TextLoader
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_text_splitters import RecursiveCharacterTextSplitter

from python_pg_bigm.helper.doc import format_docs
from python_pg_bigm.model import ApiResponse
from python_pg_bigm.model.api_response import ApiSuccessResponse
from python_pg_bigm.model.query_llm_request import QueryLlmRequest

DATA_PATH = "../../../data"
DB_PATH = "../../../chroma_db"
LLM_MODEL = "tinyllama"
EMBEDDING_MODEL = "nomic-embed-text"


class LlmServiceInterface(ABC):
    @abstractmethod
    def upload(self, file: UploadFile = File(...)) -> ApiResponse:
        pass

    @abstractmethod
    def query(self, request: QueryLlmRequest) -> ApiResponse:
        pass


class LlmService(LlmServiceInterface):
    def __init__(self):
        self.embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
        self.vectorstore = Chroma(persist_directory=DB_PATH, embedding_function=self.embeddings)
        self.llm = ChatOllama(model=LLM_MODEL)
        self.retriever = self.vectorstore.as_retriever()

        self.prompt = ChatPromptTemplate.from_template(
            """
            Answer the question based ONLY on the following context:
            
            {context}
            
            Question: {question}
            """
        )

        self.rag_chain = (
                {"context": self.retriever | format_docs, "question": RunnablePassthrough()}
                | self.prompt
                | self.llm
                | StrOutputParser()
        )

    def upload(self, file: UploadFile = File(...)) -> ApiResponse:
        if not file.filename.endswith(".txt"):
            raise HTTPException(status_code=400, detail="Only .txt files are allowed")

        if not os.path.exists(DATA_PATH):
            os.makedirs(DATA_PATH)

        file_path = os.path.join(DATA_PATH, file.filename)

        try:
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
        finally:
            file.file.close()

        loader = TextLoader(file_path)
        documents = loader.load()

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
        chunks = text_splitter.split_documents(documents)

        self.vectorstore.add_documents(chunks)

        os.remove(file_path)

        return ApiSuccessResponse(
            status=True,
            message=f"'{file.filename}' processed and added to the knowledge base",
            data=[]
        )

    def query(self, request: QueryLlmRequest) -> ApiResponse:
        try:
            retrieved_docs = self.retriever.invoke(request.query)
            answer = self.rag_chain.invoke(request.query)
            source_files = list(set([doc.metadata.get("source", "Unknown") for doc in retrieved_docs]))

            return ApiSuccessResponse(
                status=True,
                message="Success processing query",
                data={
                    "answer": answer,
                    "sources": source_files
                },
                meta={
                    "query": request.query
                }
            )
        except HTTPException as e:
            raise HTTPException(status_code=500, detail=str(e))
