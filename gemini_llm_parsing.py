from google import genai
from dotenv import load_dotenv
import os

def getClient(api_key):
    return genai.Client(api_key=api_key)

def format_email(email):
    return f"""
Subject: {email.get('subject')}
From: {email.get('from')}
To: {email.get('to')}
Date: {email.get('date')}
Body: {email.get('body')}
"""

def parseEmails(email_list):
    load_dotenv()
    client = getClient(os.getenv("GEMINI_API_KEY"))

    # Convert each email dict to a string
    email_threads = "\n\n".join([format_email(email) for email in email_list])

    # Final prompt
    user_prompt = (
        "Tist of emails is a list of emails from a client to a vendor. "
        "Please read the messages of my (chilufya@nodedropp.com) correspondence "
        "with a particular recipient. Based on our interaction as client to vendor, draft an appropriate email that:\n"
        "1. Follows up on setting up a meeting to review the updates to the website."
        "2. From the correspondence, glean what services you can upsell them and give me suggestions on what I should do as a vendor to keep their business and earn more money from them."
    )

    # Combine thread + prompt
    full_input = f"{email_threads}\n\n{user_prompt}"

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=[full_input]
    )

    if hasattr(response, "text"):
        print(response.text)
    else:
        for item in response:
            if isinstance(item, tuple):
                _, chunk = item
            else:
                chunk = item
            print(chunk.text, end="")

