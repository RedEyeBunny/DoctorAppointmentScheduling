from backend.db.database import SessionLocal
from backend.db.models import Doctor, Appointment
from datetime import datetime, timedelta
from backend.services.calender_services import create_calendar_event
from backend.services.email_service import send_email
from backend.services.notification_service import send_slack_message
from datetime import datetime
from dateutil import parser

def check_availability(doctor_name: str, date: str):
    db = SessionLocal()
    doctor = db.query(Doctor).filter_by(name=doctor_name).first()

    if doctor is None:
        return {
            "status": "error",
            "message": f"Doctor {doctor_name} not found"
        }


    start = parser.parse(date)
    end = start + timedelta(hours=8)

    appointments = db.query(Appointment).filter(
        Appointment.doctor_id == doctor.id,
        Appointment.appointment_time.between(start, end)
    ).all()

    booked_times = [a.appointment_time for a in appointments]

    all_slots = [start + timedelta(hours=i) for i in range(8)]
    available = [slot for slot in all_slots if slot not in booked_times]

    return {"available_slots": [str(s) for s in available]}


def parse_datetime(date_str: str, time_str: str):
    formats = [
        "%Y-%m-%d",
        "%d/%m/%Y",
        "%d-%m-%Y",
        "%d/%m/%y"
    ]

    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue

    raise ValueError(f"Unsupported date format: {date_str}")

def book_appointment(doctor_name, patient_name, slot_time, date):
    db = SessionLocal()
    doctor = db.query(Doctor).filter_by(name=doctor_name).first()

    if doctor is None:
        return {
            "status": "error",
            "message": f"Doctor {doctor_name} not found"
        }

    appointment = Appointment(
        doctor_id=doctor.id,
        patient_name=patient_name,
        appointment_time=parse_datetime(date, slot_time),
        reason="General Consultation"
    )
    db.add(appointment)
    db.commit()

    try:
        create_calendar_event(doctor.email, slot_time)
    except Exception as e:
        print("Calendar integration skipped:", e)
    send_email(patient_name, slot_time)

    return {"status": "confirmed"}

def generate_doctor_report(doctor_name, query_type):
    db = SessionLocal()
    doctor = db.query(Doctor).filter_by(name=doctor_name).first()

    today = datetime.now().date()

    if query_type == "today":
        count = db.query(Appointment).filter(
            Appointment.doctor_id == doctor.id,
            Appointment.appointment_time >= today
        ).count()

        report = f"You have {count} appointments today."

    send_slack_message(report)

    return {"report": report}
