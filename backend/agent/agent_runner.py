import os

from dotenv import load_dotenv
from openai import OpenAI
import json
import requests
from backend.mcp.tools import check_availability, book_appointment
from backend.utils.session_store import get_session

load_dotenv()
client = OpenAI(api_key=os.getenv("GROQ_API_KEY"), base_url="https://api.groq.com/openai/v1")

tools = [
    {
        "type": "function",
        "function": {
            "name": "book_appointment",
            "description": "Book an appointment with a doctor",
            "parameters": {
                "type": "object",
                "properties": {
                    "doctor_name": {"type": "string"},
                    "date": {"type": "string"},
                    "slot_time": {"type": "string"},
                    "patient_name": {"type": "string"}
                },
                "required": [
                    "doctor_name",
                    "date",
                    "slot_time",
                    "patient_name"
                ]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_availability",
            "description": "Check doctor availability",
            "parameters": {
                "type": "object",
                "properties": {
                    "doctor_name": {"type": "string"},
                    "date": {"type": "string"}
                },
                "required": [
                    "doctor_name",
                    "date"
                ]
            }
        }
    }
]



def call_tool_via_mcp(tool_name, args):
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": args
        },
        "id": 1
    }

    response = requests.post(
        "http://localhost:8000/mcp",
        json=payload
    )

    if response.status_code != 200:
        return {
            "status": "error",
            "message": "MCP tool execution failed"
        }

    return response.json()["result"]


def fetch_tools_for_llm():
    payload = {
        "jsonrpc": "2.0",
        "method": "tools/list",
        "id": 1
    }

    response = requests.post("http://localhost:8000/mcp", json=payload)
    discovered = response.json()["result"]

    formatted = []

    for tool in discovered:
        formatted.append({
            "type": "function",
            "function": {
                "name": tool["name"],
                "description": tool.get("description", ""),
                "parameters": tool["parameters"]
            }
        })

    return formatted

def run_agent(session_id, user_input):
    history = get_session(session_id)

    if not history:
        history.append({
            "role": "system",
            "content": "You are a medical appointment booking assistant.\n"
                        "Your job is to communicate ONLY the final result to the user.\n\n"
                        "Rules:\n"
                        "1. Never mention tools, function calls, JSON, MCP, or internal processing.\n"
                        "2. Never output raw JSON.\n"
                        "3. Do not repeat the user request.\n"
                        "4. Do not explain what you are doing.\n"
                        "5. Use the tool result as the single source of truth.\n"
                        "6. If booking succeeds, return a short confirmation sentence.\n"
                        "7. If there is an error, return a short, clear error message.\n\n"
                        "Output must be plain natural language only. Use natural, conversational language. Avoid formal or system-style phrases like - an error has occurred."
        })

    history.append({
        "role": "user",
        "content": user_input
    })
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=history,
        tools=fetch_tools_for_llm(),
        tool_choice="auto"
    )

    msg = response.choices[0].message

    if msg.tool_calls:
        tool_call = msg.tool_calls[0]
        name = tool_call.function.name
        args = json.loads(tool_call.function.arguments)

        if name == "check_availability":
            result = call_tool_via_mcp(name, args)
        elif name == "book_appointment":
            result = call_tool_via_mcp(name, args)

        history.append({
            "role": "assistant",
            "tool_calls": msg.tool_calls
        })

        history.append({
            "role": "tool",
            "tool_call_id": tool_call.id,
            "content": json.dumps(result)
        })

        final = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=history
        )

        return final.choices[0].message.content

    return msg.content
