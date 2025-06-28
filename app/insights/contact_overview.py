"""
recieve a dictionary of {
info: lead info
messages: [list of email messages]
}
using gemini llm, generate some insights based on the data
"""

import os
import json
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv

def getEmailInsights(event):
    load_dotenv()
    # get the lead info and messages from the event
    lead_info = event["info"]
    messages = event["messages"]
    # get the gemini api key from the environment
    gemini_api_key = os.environ.get("GEMINI_API_KEY")
    # get the gemini llm
    llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=gemini_api_key)
    # get the prompt template
    prompt = ChatPromptTemplate.from_template(
        """
        You are a sales lead manager. You are given a lead info and a list of messages.
        Your task is to generate insights based on the lead info and messages.
        Return the insights in this format examples, based on whatever insights you find:
        - John Mvula
  • Last message: 2024-12-10
  • Total threads: 3
  • Sentiment: Neutral
  • Follow-up needed? ❌

- Carla King
  • Last message: 2025-06-01
  • Topics: Enrollment, Staff Training
  • Action suggested: ✅ Respond to unanswered email from 5 days ago
        Lead info: {lead_info}
        Messages: {messages}
        """
    )
    # get the chain
    chain = prompt | llm | StrOutputParser()
    # get the insights
    insights = chain.invoke({"lead_info": lead_info, "messages": messages})
    # return the insights
    return {
        "statusCode": 200,
        "body": json.dumps({
            "insights": insights
        })
    }
