from fastapi import FastAPI
from pydantic import BaseModel
from backend.agent.agent_runner import run_agent

app = FastAPI()

class PromptRequest(BaseModel):
    session_id: str
    message: str

@app.post("/chat")
def chat(req: PromptRequest):
    response = run_agent(req.session_id, req.message)
    return {"response": response}
