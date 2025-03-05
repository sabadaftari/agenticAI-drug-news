import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Define the scopes required for composing emails.
SCOPES = ['https://www.googleapis.com/auth/gmail.compose']

def main():
    creds = None
    token_file = 'token.json'
    credentials_file = 'credentials.json'  # This is the file you download from Google Cloud Console.

    # check if token.json exists
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
    
    # check if the credentials are there
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # start an OAuth flow that will open your default web browser
            flow = InstalledAppFlow.from_client_secrets_file(credentials_file, SCOPES)
            creds = flow.run_local_server(port=0)
        # save the credentials to token.json
        with open(token_file, 'w') as token:
            token.write(creds.to_json())
    
    print("Credentials obtained and saved to", token_file)

if __name__ == '__main__':
    main()
