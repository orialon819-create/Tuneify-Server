# user_service.py

"""
This service handles user-related operations, like registration,
login, retrieving user info, and updating user fields or passwords.
It interacts directly with the DatabaseManager.
"""

import smtplib
from email.message import EmailMessage
import secrets
import string

# Sends a verification email containing a security code to the user
def send_email(code_to_send, email) -> None:

    # Input: code_to_send (str), email (str)
    # Output: Sends a verification email

    sender_email = "orialon819@gmail.com"
    app_password = "lelu uajg utab sbrb"  # Secret password
    receiver_email = email

    msg = EmailMessage()
    msg["Subject"] = "Verification Code"
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg.set_content(f"Code: {code_to_send}")

    # Secure SSL connection to Gmail SMTP server
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, app_password)
        server.send_message(msg)


# Generates a random 6-character verification code
def create_random_code() -> str:

    # Input: None
    # Output: Returns a randomly generated 6-character code

    alphabet = string.ascii_uppercase + string.digits
    verification_code = ''.join(secrets.choice(alphabet) for i in range(6))
    return verification_code


class UserService:
    def __init__(self, db_manager):

        # Input: db_manager (Database handler object)
        # Output: Initializes UserService instance

        self.reset_codes = {}
        self.db = db_manager

    # Input: email (str)
    # Output: Sends password reset code or error message

    def generate_reset_code(self, email) -> str:

        user = self.db.get_user_by_email(email)
        if not user:
            return "ERROR|Email not found"

        code = create_random_code()
        self.reset_codes[email] = code

        try:
            send_email(code, email)
            return "OK|Code sent"
        except Exception as e:
            return f"ERROR|Failed to send email: {str(e)}"

    # Input: email (str), input_code (str), new_password (str)
    # Output: Updates password if code is valid

    def verify_and_update_password(self, email, input_code, new_password) -> str:

        saved_code = self.reset_codes.get(email)

        if saved_code and saved_code == input_code:
            result = self.db.update_password_by_email(email, new_password)
            del self.reset_codes[email]
            return result
        else:
            return "ERROR|Invalid or expired code"

    # Input: first_name, last_name, email, username, password
    # Output: Registers new user

    def register(self, first_name, last_name, email, username, password) -> object:
        return self.db.add_user(first_name, last_name, email, username, password)

    # Input: username (str), password (str)
    # Output: Returns login verification result

    def login(self, username, password) -> object:
        return self.db.verify_user(username, password)

    # Input: username (str)
    # Output: Returns user profile data

    def get_user(self, username) -> object:
        return self.db.get_user(username)

    # Input: username (str), field (str), new_value
    # Output: Updates a specific user field

    def update_field(self, username, field, new_value) -> object:
        return self.db.update_user_field(username, field, new_value)

    # Input: username (str), new_password (str)
    # Output: Updates user password

    def update_password(self, username, new_password) -> object:
        return self.db.update_password(username, new_password)