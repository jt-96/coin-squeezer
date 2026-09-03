import os
import asyncio
import base64
import json
from email.mime.text import MIMEText
from typing import Optional
from google.adk.agents.llm_agent import Agent
from google.adk.tools import ToolContext
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import google.auth.transport.requests
from google.cloud import secretmanager
from ratelimit import limits, sleep_and_retry

@sleep_and_retry
@limits(calls=4, period=60)
def safe_rate_limit_trigger():
    pass

@sleep_and_retry
@limits(calls=5, period=60)
def safe_model_limit_trigger():
    pass

async def rate_limit_tool_callback(tool, args, tool_context):
    await asyncio.to_thread(safe_rate_limit_trigger)
    return None

async def rate_limit_model_callback(callback_context, llm_request):
    await asyncio.to_thread(safe_model_limit_trigger)
    return None

GOOGLE_USER_EMAIL_SENDER = os.environ.get("GOOGLE_USER_EMAIL_SENDER")
GOOGLE_USER_EMAIL_DESTINATION = os.environ.get("GOOGLE_USER_EMAIL_DESTINATION")
GCP_PROJECT_ID = os.environ.get("CLOUD_SQL_MYSQL_PROJECT")

# This feels like a hacky implementation, in order to obtain OAuth Refresh Token and send notification emails
# Generate a refresh token with your own Gmail OAuth creds through Google's OAuth 2.0 playground and save it in Google's Secret Manager
def fetch_oauth_config() -> dict:
    """Retrieves the GMAIL_USER_AUTH_CONFIG JSON key text directly from Secret Manager."""
    client = secretmanager.SecretManagerServiceClient()
    
    secret_path = f"projects/{GCP_PROJECT_ID}/secrets/GMAIL_USER_OAUTH_CONFIG/versions/latest"
    response = client.access_secret_version(request={"name": secret_path})

    payload_str = response.payload.data.decode("UTF-8")

    parsed_data = json.loads(payload_str)

    if isinstance(parsed_data, str):
        parsed_data = json.loads(parsed_data)
        
    return parsed_data

def send_gmail_message(subject: str, email_body: str, tool_context: Optional[ToolContext] = None) -> str:
    """Sends an email using the Gmail API via OAuth credentials provided by the runtime context."""
    try:
        oauth_data = fetch_oauth_config()

        info = {
            "refresh_token": oauth_data["refresh_token"],
            "client_id": oauth_data["client_id"],
            "client_secret": oauth_data["client_secret"],
            "token_uri": "https://www.googleapis.com/auth/gmail.send" 
        }

        creds = Credentials.from_authorized_user_info(
            info, 
            scopes=['https://www.googleapis.com/auth/gmail.send']
        )

        request = google.auth.transport.requests.Request()
        creds.refresh(request)

        service = build('gmail', 'v1', credentials=creds)
        
        safe_subject = str(subject)
        safe_body = str(email_body)

        message = MIMEText(safe_body)
        message['To'] = GOOGLE_USER_EMAIL_DESTINATION
        message['From'] = GOOGLE_USER_EMAIL_SENDER
        message['Subject'] = safe_subject

        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        create_message = {'raw': encoded_message}

        service.users().messages().send(userId="me", body=create_message).execute()
        return "Email Sent!"
        
    except Exception as e:
        return f"Failed to send email due to: {str(e)}"

email_agent = Agent(
    model='gemini-3.5-flash',
    name='email_agent',
    description='An assistant in charge of email parsing and communications.',
    instruction=f"""You are an email assistant

    Your role is to parse the data recieved from the previous agent in the order of execution and send it through email, using the connected MCP tool.

    This data {{parsed_data}} should be formatted as a list, containing the name of the product and each price from the stores.

    From: {GOOGLE_USER_EMAIL_SENDER}
    Recipient: {GOOGLE_USER_EMAIL_DESTINATION}
    Subject: "Coin Squeezer Notification!"
    Body: "There are new offers to check! *PARSED LIST GOES HERE*"
    
    If there's an error during the operation, say so, otherwise respond with "Email Sent!" to finish.
    """,
    tools=[send_gmail_message],
    before_tool_callback=rate_limit_tool_callback,
    before_model_callback=rate_limit_model_callback
)
