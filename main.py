from pydantic import BaseModel
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware

from rag_main import RagPipeline


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.rag_pipeline = RagPipeline(name="rag_pipeline")
    yield

app = FastAPI(lifespan=lifespan)

origins = [
    "http://localhost",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods (GET, POST, etc.)
    allow_headers=["*"], # Allows all headers
)




class UserInput(BaseModel):
    input: str

class RagResponse(BaseModel):
    claim: str
    verification: str


def get_rag_pipeline(request: Request):
    return request.app.state.rag_pipeline


@app.get("/")
async def root():
    return {"message": "Welcome to the political claims verification application. Enjoy your stay!"}

@app.post("/validate_claim", response_model=RagResponse)
async def validate_claim(claim: UserInput, rag_pipeline: RagPipeline = Depends(get_rag_pipeline)):
    claim = claim.input
    verification = rag_pipeline.process_claim(claim)
    return {
        "claim": claim,
        "verification": verification
    }