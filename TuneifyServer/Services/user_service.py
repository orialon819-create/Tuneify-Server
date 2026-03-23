"""
user_service.py

This service handles user-related operations, like registration,
login, retrieving user info, and updating user fields or passwords.
It interacts directly with the DatabaseManager.
"""
import smtplib
from email.message import EmailMessage
import secrets
import string

# Connects to Google's SMTP server to send a security code to the user's email
def send_email(code_to_send, email):
    sender_email = "orialon819@gmail.com"
    app_password = "lelu uajg utab sbrb" # Secret password
    receiver_email = email

    msg = EmailMessage()
    msg["Subject"] = "Verification Code"
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg.set_content(f"Code: {code_to_send}")

    # Establishes a secure SSL connection to ensure the email content is encrypted
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender_email, app_password)
        server.send_message(msg)

# Generates a strong 6-character code for password resets
def create_random_code():
    alphabet = string.ascii_uppercase + string.digits
    verification_code = ''.join(secrets.choice(alphabet) for i in range(6))
    return verification_code


class UserService:
    def __init__(self, db_manager):
        self.reset_codes = {}
        self.db = db_manager

    # Orchestrates the "Forgot Password" flow: verifies email, generates code, and sends it
    def generate_reset_code(self, email):
        # 1. Check if user exists in DB first
        user = self.db.get_user_by_email(email)
        if not user:
            return "ERROR|Email not found"

        # 2. Use the random generator to create the unique code
        code = create_random_code()

        # 3. Save it to our 'Memory' dictionary for later verification
        self.reset_codes[email] = code

        # 4. Attempt to send the email via the SMTP function
        try:
            send_email(code, email)
            return "OK|Code sent"
        except Exception as e:
            return f"ERROR|Failed to send email: {str(e)}"

    # Compares the user's input code with the one in memory and updates the password if correct
    def verify_and_update_password(self, email, input_code, new_password):
        # 1. Retrieve the code previously sent to this email
        saved_code = self.reset_codes.get(email)

        if saved_code and saved_code == input_code:
            # 2. Code match confirmed: Update the database with the new password
            result = self.db.update_password_by_email(email, new_password)
            # 3. Security cleanup: Delete the code so it cannot be reused
            del self.reset_codes[email]
            return result
        else:
            return "ERROR|Invalid or expired code"

    # Handles new user account creation by passing data to the database layer
    def register(self, first_name, last_name, email, username, password):
        return self.db.add_user(first_name, last_name, email, username, password)

    # Validates credentials by checking the provided username and password against the DB
    def login(self, username, password):
        return self.db.verify_user(username, password)

    # Fetches the full profile data for a specific user
    def get_user(self, username):
        return self.db.get_user(username)

    # Allows for dynamic updates of specific user profile fields (like email or name)
    def update_field(self, username, field, new_value):
        return self.db.update_user_field(username, field, new_value)

    # Updates the password directly for an already logged-in user
    def update_password(self, username, new_password):
        return self.db.update_password(username, new_password)