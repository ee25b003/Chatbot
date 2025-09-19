import os
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory

load_dotenv()

app = Flask(__name__)

llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.1-8b-instant",
    temperature=0.7,
)

prompt = ChatPromptTemplate.from_messages(
    [
        ("system", "You are a helpful assistant."),
        MessagesPlaceholder("history"),
        ("human", "{input}"),
    ]
)

chain = prompt | llm

user_histories = {}

def get_user_history(user_id: str):
    if user_id not in user_histories:
        user_histories[user_id] = ChatMessageHistory()
    return user_histories[user_id]

runnable = RunnableWithMessageHistory(
    chain,
    get_user_history,
    input_messages_key="input",
    history_messages_key="history",
)

@app.route("/whatsapp", methods=["POST"])
def whatsapp_reply():
    incoming_msg = request.form.get("Body")
    user_number = request.form.get("From")
    print(f"{user_number} said: {incoming_msg}")

    try:
        response = runnable.invoke(
            {"input": incoming_msg},
            config={"configurable": {"session_id": user_number}},
        )
        response_text = response.content
    except Exception as e:
        print("Error:", e)
        response_text = "⚠️ Sorry, something went wrong with the AI model."

    twilio_resp = MessagingResponse()
    twilio_resp.message(response_text)
    return str(twilio_resp)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
