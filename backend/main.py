from fastapi import FastAPI
from pydantic import BaseModel
from backend.agent.agent_runner import run_agent
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class PromptRequest(BaseModel):
    session_id: str
    message: str


@app.post("/chat")
def chat(req: PromptRequest):
    response = run_agent(req.session_id, req.message)
    return {"response": response}
