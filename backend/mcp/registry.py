from .tools import book_appointment, check_availability

TOOL_REGISTRY = {
    "book_appointment": {
        "func": book_appointment,
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
    },
    "check_availability": {
        "func": check_availability,
        "description": "Check doctor availability",
        "parameters": {
            "type": "object",
            "properties": {
                "doctor_name": {"type": "string"},
                "date": {"type": "string"}
            },
            "required": ["doctor_name", "date"]
        }
    }
}
