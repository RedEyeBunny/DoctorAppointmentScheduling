import os

from dotenv import load_dotenv
from openai import OpenAI

from backend.mcp.tools import check_availability, book_appointment
from backend.utils.session_store import get_session

load_dotenv()
client = OpenAI(api_key=os.getenv("GROQ_API_KEY"), base_url="https://api.groq.com/openai/v1")

tools = [
    {
        "type": "function",
        "function": {
            "name": "check_availability",
            "parameters": {
                "type": "object",
                "properties": {
                    "doctor_name": {"type": "string"},
                    "date": {"type": "string"}
                },
                "required": ["doctor_name", "date"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "book_appointment",
            "parameters": {
                "type": "object",
                "properties": {
                    "doctor_name": {"type": "string"},
                    "patient_name": {"type": "string"},
                    "slot_time": {"type": "string"},
                    "date": {"type": "string"}
                },
                "required": ["doctor_name", "patient_name", "slot_time", "date"]
            }
        }
    }
]

def run_agent(session_id, user_input):
    history = get_session(session_id)
    history.append({"role": "user", "content": user_input})

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=history,
        tools=tools,
        tool_choice="auto"
    )

    msg = response.choices[0].message

    if msg.tool_calls:
        tool_call = msg.tool_calls[0]
        name = tool_call.function.name
        args = eval(tool_call.function.arguments)

        if name == "check_availability":
            result = check_availability(**args)
        elif name == "book_appointment":
            result = book_appointment(**args)

        history.append({"role": "tool", "content": str(result), "tool_call_id": tool_call.id})

        final = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=history
        )

        return final.choices[0].message.content

    return msg.content
