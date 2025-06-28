import os
import webbrowser
import msal
from dotenv import load_dotenv

MS_GRAPH_BASE_URL= "https://graph.microsoft.com/v1.0"

def getAcessToken(app_id, client_secret, scopes):
    client = msal.ConfidentialClientApplication(
        client_id=app_id,
        client_credential=client_secret,
        authority="https://login.microsoftonline.com/common"
    )

    # check if there is a refresh token stored
    refresh_token = None
    if os.path.exists("refresh_token.txt"):
        with open("refresh_token.txt", "r") as f:
            refresh_token = f.read().strip()
    
    if refresh_token:
        # get new access token with refresh token
        token_response = client.acquire_token_by_refresh_token(refresh_token, scopes=scopes)
    else:
        # no refresh token, use auth flow
        auth_request_url = client.get_authorization_request_url(scopes, prompt="select_account")
        webbrowser.open(auth_request_url)
        auth_code = input("Enter the authorization code: ")

        if not auth_code:
            raise ValueError("No authorization code provided.")
        
        token_response = client.acquire_token_by_authorization_code(code=auth_code, scopes=scopes)
    
    if "access_token" in token_response:
        # store the refresh token
        if "refresh_token" in token_response:
            with open("refresh_token.txt", "w") as f:
                f.write(token_response["refresh_token"])
        return token_response["access_token"]

    else:
        raise Exception("Failed to acquire access token" + str(token_response))

def main():
    load_dotenv()
    APPLICATION_ID = os.getenv("APPLICATION_ID")
    CLIENT_SECRET = os.getenv("MS_CLIENT_SECRET")
    SCOPES = ["User.Read", "Mail.ReadWrite", "Mail.Send"]

    try:
        access_token = getAcessToken(app_id=APPLICATION_ID, client_secret=CLIENT_SECRET, scopes=SCOPES)
        headers = {
            "Authorization": "Bearer " + access_token
        }
        # print(headers)
        print("Access token acquired")
    except Exception as e:
        print("Error: ", e)

main()
