from app.email.outlook_auth import get_headers
from app.email.outlook_client import fetch_emails_from_sender, emails_to_dataframe, get_user_profile
from app.contacts.load_emails import getEmailLeads
from app.insights.contact_overview import getEmailInsights

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_vertexai import VertexAIEmbeddings
from langchain_core.vectorstores import InMemoryVectorStore
from langchain import hub
from langchain.chat_models import init_chat_model
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

import os
import json
from dotenv import load_dotenv

load_dotenv()

# Initialize LLM, embeddings, vector store
gemini_api_key = os.environ.get("GEMINI_API_KEY")
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", google_api_key=gemini_api_key)
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=gemini_api_key)
vector_store = InMemoryVectorStore(embeddings)

def safe_list_to_string(data) -> str:
    if isinstance(data, list):
        return json.dumps(data) if all(isinstance(item, dict) for item in data) else ", ".join(str(item) for item in data)
    return str(data)

def create_document(row):
    email = row.get("Email")
    if not email:
        print(f"Skipping row with missing email: {row}")
        return None
    messages = fetch_emails_from_sender(get_headers(), email)
    return Document(page_content=safe_list_to_string(messages), metadata=row.to_dict()) if messages else None

if __name__ == "__main__":
    headers = get_headers()
    user = get_user_profile(headers)
    print(f"Signed in as: {user['name']} <{user['email']}>")

    email_list_file_path = input("Please provide path to CSV file of leads: ")
    leads = getEmailLeads(email_list_file_path)

    email_ledger = []
    email_documents = []

    print(f"\n🔍 Fetching emails for each contact...\n")
    leads.apply(lambda row: email_ledger.append({
        "info": row,
        "messages": fetch_emails_from_sender(headers, row["Email"])
    }), axis=1)

    print(f"\n📊 Generating insights...\n")
    for lead in email_ledger:
        insights = getEmailInsights(event=lead)
        clean_output = json.loads(insights["body"])
        print(clean_output["insights"])

    # Convert emails into Document objects
    for lead in email_ledger:
        doc = Document(
            page_content=safe_list_to_string(lead["messages"]),
            metadata=lead["info"].to_dict()
        )
        email_documents.append(doc)

    # Split documents
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200, add_start_index=True)
    all_splits = text_splitter.split_documents(email_documents)
    print(f"✅ Split {len(email_documents)} emails into {len(all_splits)} sub-documents")

    # Index into vector store
    vector_store.add_documents(all_splits)

    # Setup RAG prompt
    prompt = hub.pull("rlm/rag-prompt")

    # Start simple RAG Q&A loop
    while True:
        user_query = input("\n💬 Ask a question about your emails (or type 'exit'): ").strip()
        if user_query.lower() == "exit":
            break

        retrieved_docs = vector_store.similarity_search(user_query, k=5)
        docs_content = "\n\n".join(doc.page_content for doc in retrieved_docs)

        prompt_msgs = prompt.invoke({"question": user_query, "context": docs_content})
        response = llm.invoke(prompt_msgs)

        print(f"-------------------------------------------------------")
        print(f"\n📬 Answer:\n{response.content}")
        print(f"-------------------------------------------------------")

