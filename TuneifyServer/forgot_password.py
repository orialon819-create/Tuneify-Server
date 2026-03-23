import smtplib
from email.message import EmailMessage
import secrets
import string

def send_email(code_to_send, email):
    sender_email = "orialon819@gmail.com"
    app_password = "lelu uajg utab sbrb"
    receiver_email = email

    msg = EmailMessage()
    msg["Subject"] = "Verification Code"
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg.set_content(f"Code: {code_to_send}")

    # Send email securely
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, app_password)
        server.send_message(msg)


def create_random_code():
    alphabet = string.ascii_uppercase + string.digits
    verification_code = ''.join(secrets.choice(alphabet) for i in range(6))
    return verification_code