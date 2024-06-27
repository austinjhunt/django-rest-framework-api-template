import base64
import logging
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from django.conf import settings
from google.oauth2 import service_account
from googleapiclient.discovery import build
from jinja2 import Environment, FileSystemLoader, select_autoescape
from django.contrib.auth.models import User
from api.models import Profile

logger = logging.getLogger(settings.PRIMARY_LOGGER_NAME)

##############################
## SETUP JINJA ENVIRONMENT ###
##############################
email_template_dir = os.path.join(os.path.dirname(__file__), "templates", "email")
jinja_env = Environment(
    loader=FileSystemLoader(email_template_dir),
    autoescape=select_autoescape(["html", "xml"]),
)


def send_email(recipient, subject, body):
    """
    Sends an email using the Gmail API.

    Args:
        recipient (str): The email address of the recipient.
        subject (str): The subject of the email.
        body (str): The body of the email.
    Returns:
        None
    """
    # do not send email if recipient domain is @example.com
    if "test" in recipient or "example.com" in recipient:
        logger.info(
            {
                "action": "send_email",
                "recipient": recipient,
                "subject": subject,
                "body": body,
                "message": "Not sending email to test recipient",
            }
        )
        return None

    logger.info({"action": "send_email", "recipient": recipient, "subject": subject, "body": body})
    try:
        SCOPES = ["https://www.googleapis.com/auth/gmail.send"]
        credentials = service_account.Credentials.from_service_account_info(
            {
                "type": "service_account",
                "project_id": settings.GMAIL_API_PROJECT_ID,
                "private_key_id": settings.GMAIL_API_SERVICE_ACCOUNT_PRIVATE_KEY_ID,
                "private_key": settings.GMAIL_API_SERVICE_ACCOUNT_PRIVATE_KEY,
                "client_email": settings.GMAIL_API_SERVICE_ACCOUNT_CLIENT_EMAIL,
                "client_id": settings.GMAIL_API_SERVICE_ACCOUNT_CLIENT_ID,
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": settings.GMAIL_API_SERVICE_ACCOUNT_CLIENT_X509_CERT_URL,
                "universe_domain": "googleapis.com",
            },
            scopes=SCOPES,
        )
        delegated_credentials = credentials.with_subject(settings.SEND_FROM_EMAIL)
        service = build("gmail", "v1", credentials=delegated_credentials)
        message = MIMEMultipart("alternative")
        message["to"] = recipient
        message["subject"] = subject
        message["from"] = f"{settings.APP_NAME} <{settings.SEND_FROM_EMAIL}>"

        # Load the Jinja template
        template = jinja_env.get_template("master.html")

        # Render the template
        # Render the template with variables
        ## allow body to be HTML
        html_body = template.render(
            title=subject,
            header=subject,
            content=body,
            frontend_url=settings.FRONTEND_URL,
            frontend_brand_logo_image_url=settings.FRONTEND_BRAND_LOGO_IMAGE_URL,
            app_name=settings.APP_NAME,
        )
        # Attach both plain text and HTML versions of the message.
        part1 = MIMEText(body, "plain")
        part2 = MIMEText(html_body, "html")

        # part1 will display if HTML disabled on recipient client
        message.attach(part1)
        # part2 will display if HTML enabled on recipient client
        message.attach(part2)
        raw = base64.urlsafe_b64encode(message.as_bytes())
        raw = raw.decode()
        body = {"raw": raw}
        message = service.users().messages().send(userId="me", body=body).execute()
        logger.info(
            {
                "action": "send_email",
                "message_sent": {
                    "id": message["id"],
                    "threadId": message["threadId"],
                    "recipient": recipient,
                    "body": body,
                    "subject": subject,
                    "userId": "me",
                },
            }
        )
        return message
    except Exception as e:
        logger.error({"action": "send_email", "error": str(e)})
        return None


def send_password_reset_email(recipient, first_name, subject, reset_link):
    """
    Sends a password reset email to the specified recipient.

    Args:
        recipient (str): The email address of the recipient.
        first_name (str): The first name of the recipient.
        subject (str): The subject of the email.
        reset_link (str): The password reset link.
    Returns:
        message (dict): The response from the Gmail API.
    """
    logger.info(
        {
            "action": "send_password_reset_email",
            "recipient": recipient,
            "first_name": first_name,
            "subject": subject,
            "reset_link": reset_link,
        }
    )
    try:
        # Load the Jinja template
        template = jinja_env.get_template("password_reset.html")
        # Render the template with variables
        html_body = template.render(
            reset_link=reset_link, first_name=first_name, app_name=settings.APP_NAME
        )
        return send_email(
            recipient=recipient,
            subject=subject,
            body=html_body,
        )
    except Exception as e:
        logger.error({"action": "send_password_reset_email", "error": str(e)})
        return None


def send_activate_account_email(recipient, first_name, subject, activate_link):
    """
    Sends an account activation email to the specified recipient.

    Args:
        recipient (str): The email address of the recipient.
        first_name (str): The first name of the recipient.
        subject (str): The subject of the email.
        activate_link (str): The account activation link.
    Returns:
        message (dict): The response from the Gmail API.
    """
    logger.info(
        {
            "action": "send_activate_account_email",
            "recipient": recipient,
            "first_name": first_name,
            "subject": subject,
            "activate_link": activate_link,
        }
    )
    try:
        # Load the Jinja template
        template = jinja_env.get_template("activate_account.html")
        # Render the template with variables
        html_body = template.render(
            activate_link=activate_link, first_name=first_name, app_name=settings.APP_NAME
        )
        return send_email(
            recipient=recipient,
            subject=subject,
            body=html_body,
        )
    except Exception as e:
        logger.error({"action": "send_activate_account_email", "error": str(e)})
        return None


def send_contact_us_received_acknowledgement_email(recipient, first_name, message, submitted_at):
    """When the contact us form is submitted on the home page,
    we save a ContactFormSubmission instance and send the user an email to acknowledge receipt of their message, with a copy of their message for their records.
    """
    logger.info(
        {
            "action": "send_contact_us_received_acknowledgement_email",
            "recipient": recipient,
            "first_name": first_name,
            "message": message,
            "submitted_at": submitted_at,
        }
    )
    try:
        template = jinja_env.get_template("contact_us_received_acknowledgement.html")
        html_body = template.render(
            first_name=first_name,
            message=message,
            submitted_at=submitted_at,
            app_name=settings.APP_NAME,
            contact_email=settings.CONTACT_EMAIL,
        )
        return send_email(
            recipient=recipient,
            subject=f"Thank You For Contacting {settings.APP_NAME}!",
            body=html_body,
        )
    except Exception as e:
        logger.error({"action": "send_contact_us_received_acknowledgement_email", "error": str(e)})
        return None


def send_payment_complete_confirmation_email(
    recipient, first_name, subject, payment_amount  # CHANGEME: add args re: what is being paid for
):
    """
    Sends an email to the user confirming successful payment for a course section.
    """
    logger.info(
        {
            "action": "send_payment_complete_confirmation_email",
            "recipient": recipient,
            "first_name": first_name,
            "subject": subject,
            "payment_amount": payment_amount,
        }
    )
    try:
        template = jinja_env.get_template("payment_complete_confirmation.html")
        html_body = template.render(
            first_name=first_name,
            payment_amount=payment_amount,
            app_name=settings.APP_NAME,
            contact_email=settings.CONTACT_EMAIL,
            frontend_url=settings.FRONTEND_URL,
        )
        return send_email(
            recipient=recipient,
            subject=subject,
            body=html_body,
        )
    except Exception as e:
        logger.error({"action": "send_payment_complete_confirmation_email", "error": str(e)})
        return None


##############################
## USER CREATION UTILITIES ###
##############################


def create_user(username, email, first_name, last_name, password, is_active=False):
    # create user and profile
    user = User.objects.create_user(
        username=username,
        email=email,
        first_name=first_name,
        last_name=last_name,
        password=password,
    )
    user.is_active = is_active
    user.save()
    profile = Profile.objects.create(user=user)
    profile.save()

    return user


#####################################
###### SERIALIZER UTILITIES #########
#####################################

def get_simple_serializer_error(serializer):
    # flatten the error messages
    error_message = ""
    for key, value in serializer.errors.items():
        error_message += f"{value[0]} "
    return error_message.strip()