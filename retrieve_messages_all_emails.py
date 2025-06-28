import os
import httpx
from dotenv import load_dotenv
from ms_graph import getAcessToken, MS_GRAPH_BASE_URL

def display_user_email(headers):
    """Fetch and display the signed-in user's email address."""
    me_endpoint = f"{MS_GRAPH_BASE_URL}/me"
    response = httpx.get(me_endpoint, headers=headers)
    if response.status_code == 200:
        user_info = response.json()
        print(f"\n📧 Signed in as: {user_info.get('displayName')} <{user_info.get('mail') or user_info.get('userPrincipalName')}>\n")
    else:
        raise Exception(f"Failed to get user info: {response.text}")

def main():
    load_dotenv()
    APPLICATION_ID = os.getenv("APPLICATION_ID")
    CLIENT_SECRET = os.getenv("MS_CLIENT_SECRET")
    SCOPES = ["User.Read", "Mail.ReadWrite", "Mail.Send"]

    endpoint = f'{MS_GRAPH_BASE_URL}/me/messages'

    try:
        access_token = getAcessToken(app_id=APPLICATION_ID, client_secret=CLIENT_SECRET, scopes=SCOPES)
        headers = {
            "Authorization": "Bearer " + access_token
        }

        # Show the signed-in user's email
        display_user_email(headers)

        for i in range(0, 4, 2):
            params = {
                "$top": 2,
                "$select": "*",
                "$skip": 1,
                "$orderby": "receivedDateTime desc"
            }

            response = httpx.get(endpoint, headers=headers, params=params)

            if response.status_code != 200:
                raise Exception(f'Failed to retrieve emails: {response.text}')
            json_response = response.json()

            for mail_message in json_response.get('value', []):
                if mail_message['isDraft']:
                    print('Subject: ', mail_message['subject'])
                    print('To:', mail_message['toRecipients'])
                    print('Is Read:', mail_message['isRead'])
                    print('Received Date Time: ', mail_message['receivedDateTime'])
                    print()
                else:
                    print('Subject: ', mail_message['subject'])
                    print('To:', mail_message['toRecipients'])
                    print('From:', mail_message['from']['emailAddress']['name'], 
                          f"({mail_message['from']['emailAddress']['address']})")
                    print('Received Date Time: ', mail_message['receivedDateTime'])
                    print()
            print('-' * 150)
    except httpx.HTTPStatusError as e:
        print(f'HTTP error: {e}')
    except Exception as e:
        print(f'Error: {e}')

main()
