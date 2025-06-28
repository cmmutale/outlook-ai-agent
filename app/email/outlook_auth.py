import os
import msal
from dotenv import load_dotenv

MS_GRAPH_BASE_URL = "https://graph.microsoft.com/v1.0"

def get_access_token(app_id, client_secret, scopes):
    client = msal.ConfidentialClientApplication(
        client_id=app_id,
        client_credential=client_secret,
        authority="https://login.microsoftonline.com/common"
    )

    refresh_token = None
    if os.path.exists("refresh_token.txt"):
        with open("refresh_token.txt", "r") as f:
            refresh_token = f.read().strip()

    if refresh_token:
        token_response = client.acquire_token_by_refresh_token(refresh_token, scopes=scopes)
    else:
        auth_url = client.get_authorization_request_url(scopes, prompt="select_account")
        print(f"Open this URL and sign in: {auth_url}")
        auth_code = input("Enter the authorization code: ").strip()
        token_response = client.acquire_token_by_authorization_code(code=auth_code, scopes=scopes)

    if "access_token" in token_response:
        if "refresh_token" in token_response:
            with open("refresh_token.txt", "w") as f:
                f.write(token_response["refresh_token"])
        return token_response["access_token"]

    raise Exception(f"Token acquisition failed: {token_response}")


def get_headers():
    load_dotenv()
    app_id = os.getenv("APPLICATION_ID")
    client_secret = os.getenv("MS_CLIENT_SECRET")
    scopes = ["User.Read", "Mail.ReadWrite", "Mail.Send"]
    access_token = get_access_token(app_id, client_secret, scopes)
    return {"Authorization": f"Bearer {access_token}"}
