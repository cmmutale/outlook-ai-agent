import pandas as pd
import os
from retrieve_messages_email_address import fetch_emails_from_sender, getHeaders, convertToDf

def getCSVList(file):
    email_list = pd.read_csv(file)
    return email_list

def retrieveEmailsForEachSender(row, header):
    print(f"{row['Name']} | {row["Email"]}")
    emails = fetch_emails_from_sender(header, row["Email"])
    # if emails is none return print nothing found
    if (emails is None):
        print("No emails found")
    print(convertToDf(emails))

def main():
    file = os.path.join(os.getcwd(), 'email-list.csv')
    email_list = getCSVList(file)
    print(email_list)
    headers = getHeaders()
    email_list.apply(lambda row: retrieveEmailsForEachSender(row, header=headers), axis=1)

main()

