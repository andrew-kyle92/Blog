import smtplib
from email.message import EmailMessage
from email.headerregistry import Address
from email.utils import make_msgid
from dotenv import dotenv_values

config = dotenv_values(".env")


# noinspection PyStringFormat
class SendEmail:

    def __init__(self):
        self.email = "andrewkyle@andrewkyle.dev"
        self.password = config.get("EMAIL_PASSWORD")
        self.smtp_server = "smtp.gmail.com"
        self.smtp_port = 587

    def send_email(self, sender_data):
        sender_username = sender_data["email"].split("@")[0]
        sender_domain = sender_data["email"].split("@")[1]
        if sender_data['name'] == "":
            subject = f"Incoming email from Blog Site"
        else:
            subject = f"Incoming email from Blog Site sent by {sender_data['name']}"

        # Message Container
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = Address(sender_data["name"], addr_spec=sender_data["email"])
        msg['To'] = Address(display_name="Andrew Kyle",
                            addr_spec="andrewkyle@andrewkyle.dev")
        msg.add_alternative(f"""
        <!DOCTYPE html>
        <html>
            <head></head>
            <body>
                {sender_data["msg"]}
                <br>
                <p>{sender_data["phone"]}</p>
                <p>{sender_data["email"]}</p>
            </body>
        </html>
        """, subtype='html')

        with smtplib.SMTP(self.smtp_server, self.smtp_port) as connection:
            connection.starttls()
            connection.login(self.email, self.password)
            connection.send_message(msg=msg)

        print("Email sent successfully")