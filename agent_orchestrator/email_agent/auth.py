import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Define the scope matching what you picked on your OAuth Consent Screen.
# We use the strict 'gmail.send' scope for maximum security.
SCOPES = ['https://googleapis.com']

def get_workspace_access_token():
    """
    Checks for a valid stored user token. If missing or expired, 
    pops open a browser to log the user in and fetch a fresh Access Token.
    """
    creds = None
    
    # token.json stores the user's access and refresh tokens after first login
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        
    # If there are no valid credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            # Silently refresh the token if it expired
            print("Access token expired. Refreshing token silently...")
            creds.refresh(Request())
        else:
            # Missing token. Start the local server to trigger the browser pop-up
            print("No valid token found. Opening browser for Google login...")
            flow = InstalledAppFlow.from_client_secrets_file(
                './secrets/email_oauth_credentials.json', SCOPES
            )
            # This creates a short-lived local server to listen for Google's code
            creds = flow.run_local_server(port=0)
            
        # Save the credentials for the next run so you don't login every time
        with open('token.json', 'w') as token_file:
            token_file.write(creds.to_json())
            
    # Return the clean text access token string needed for the ADK tool header
    return creds.token

if __name__ == '__main__':
    # Test the token extraction
    try:
        token = get_workspace_access_token()
        print("\n🎉 Success!")
        print(f"Your Google Workspace Access Token is: {token[:15]}...[TRUNCATED]")
        print("You can safely feed this token right into your ADK Agent.")
    except Exception as e:
        print(f"\n❌ Error authenticating: {e}")
