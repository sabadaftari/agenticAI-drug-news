from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
import base64
from email.mime.text import MIMEText

from config import (
    SLACK_BOT_TOKEN,
    SLACK_USER_ID,
    GMAIL_CREDENTIALS_JSON
)

def send_slack_dm(message: str) -> None:
    slack_bot_token = SLACK_BOT_TOKEN
    slack_user_id = SLACK_USER_ID  # This is the Slack user ID to receive the DM

    client = WebClient(token=slack_bot_token)
    try:
        
        response = client.conversations_open(users=[slack_user_id]) # open a conversation with the user
        channel_id = response["channel"]["id"]
        
        client.chat_postMessage(channel=channel_id, text=message) # send the DM
        print(response)
    except SlackApiError as e:
        print(f"Error sending Slack DM: {e.response['error']}")

def create_gmail_draft(message: str, subject: str = "Stock Summary", to: str = None) -> None:

    gmail_credentials_json = GMAIL_CREDENTIALS_JSON

    try:
        # load credentials from the JSON file
        creds = Credentials.from_authorized_user_file(
            gmail_credentials_json,
            scopes=["https://www.googleapis.com/auth/gmail.compose"]
        )
        service = build("gmail", "v1", credentials=creds)

        # create a MIMEText email message
        message_obj = MIMEText(message)
        message_obj["to"] = to if to else ""
        message_obj["subject"] = subject
        raw_message = base64.urlsafe_b64encode(message_obj.as_bytes()).decode()

        draft = {"message": {"raw": raw_message}} 
        draft_response = service.users().drafts().create(userId="me", body=draft).execute() # make the draft message
        print(draft_response)
    except Exception as e:
        print(f"Error creating Gmail draft: {e}")
