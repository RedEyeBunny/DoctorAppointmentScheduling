import smtplib
from backend.config import GMAIL_USER, GMAIL_PASS

def send_email(patient_name, slot_time):
    subject = "Appointment Confirmed"
    body = f"Your appointment is confirmed at {slot_time}"
    message = f"Subject: {subject}\n\n{body}"

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_USER, GMAIL_PASS)
        server.sendmail(GMAIL_USER, GMAIL_USER, message)
