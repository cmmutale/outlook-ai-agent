import pandas as pd

def printEmailRow(row):
    print(f" - {row['Name']} <{row['Email']}>")   

def getEmailLeads(filePath):
    df = pd.read_csv('email-list.csv')
    # emailLeads = df[df['Email'] == 'Email']
    print(f"Loaded {len(df)} contacts")
    df.apply(printEmailRow, axis=1)
    return df
