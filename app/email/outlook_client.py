import httpx
import pandas as pd
from app.utils.html_parser import html_to_text
from app.email.outlook_auth import MS_GRAPH_BASE_URL

def get_user_profile(headers):
    endpoint = f"{MS_GRAPH_BASE_URL}/me"
    response = httpx.get(endpoint, headers=headers)
    response.raise_for_status()
    data = response.json()
    return {
        "name": data.get("displayName"),
        "email": data.get("mail") or data.get("userPrincipalName")
    }

def fetch_emails_from_sender(headers, sender_email, max_results=20):
    print(f"fetching from: {sender_email}")
    filter_query = f"(from/emailAddress/address) eq '{sender_email}'"
    endpoint = f"{MS_GRAPH_BASE_URL}/me/messages"
    params = {
        "$top": max_results,
        "$filter": filter_query,
        "$select": "subject,from,toRecipients,receivedDateTime,isRead,isDraft,body"
    }

    response = httpx.get(endpoint, headers=headers, params=params)
    response.raise_for_status()

    messages = response.json().get("value", [])
    if not messages:
        # print(f"No messages found from {sender_email}")
        print(f"❌ {sender_email} no emails\n\n")
        return []
    
    print(f"✅ {sender_email} — {len(messages)} emails\n\n")

    return [
        {
            "subject": msg["subject"],
            "from": (msg["from"]["emailAddress"]["name"], msg["from"]["emailAddress"]["address"]),
            "to": [r["emailAddress"]["address"] for r in msg.get("toRecipients", [])],
            "received": msg["receivedDateTime"],
            "message": html_to_text(msg["body"]["content"])
        }
        for msg in messages
    ]

def emails_to_dataframe(messages):
    return pd.DataFrame(messages)
