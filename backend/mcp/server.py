from fastapi import APIRouter
from pydantic import BaseModel
from typing import Any, Dict
from .registry import TOOL_REGISTRY

router = APIRouter()


class JSONRPCRequest(BaseModel):
    jsonrpc: str
    method: str
    params: Dict[str, Any] | None = None
    id: int


@router.post("/mcp")
def handle_rpc(request: JSONRPCRequest):

    if request.method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "result": [
                {
                    "name": name,
                    "description": meta["description"],
                    "parameters": meta["parameters"]
                }
                for name, meta in TOOL_REGISTRY.items()
            ],
            "id": request.id
        }

    if request.method == "tools/call":
        tool_name = request.params["name"]
        arguments = request.params["arguments"]

        if tool_name not in TOOL_REGISTRY:
            return {
                "jsonrpc": "2.0",
                "error": {"message": "Tool not found"},
                "id": request.id
            }

        result = TOOL_REGISTRY[tool_name]["func"](**arguments)

        return {
            "jsonrpc": "2.0",
            "result": result,
            "id": request.id
        }

    return {
        "jsonrpc": "2.0",
        "error": {"message": "Invalid method"},
        "id": request.id
    }
