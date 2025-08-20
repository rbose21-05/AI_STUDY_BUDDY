from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import AIMessage
import os

template = """ 
You are a helpful, friendly AI assistant. 
Always give clear, detailed answers to the user's questions.
If you are unsure, try to give a thoughtful guess rather than refusing.
You are a friendly tutor.

The user will upload a pdf file from where you will receive the txt. 
You have to analyse it and prepare a study plan as asked.

Here is the conversation history so far:
{context}

Question: {question}

Answer:
"""

# ⚡ Use Gemini instead of Ollama
model = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",   # or gemini-1.5-pro
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model



def handle_conversation():
    # Load PDF text context (previously extracted into study_guide.txt)
    try:
        with open("study_guide.txt", "r", encoding="utf-8") as f:
            context = f.read()
    except FileNotFoundError:
        context = ""  # if file missing, start fresh

    print("Welcome to the AI chat, type 'exit' to quit")

    while True:
        user_input = input("\nYou: ")
        if user_input.lower() == "exit":
            break

        # Run the chain with context + question
        result = chain.invoke({
            "context": context,
            "question": user_input
        })

        # Extract just the text reply
        bot_reply = result.content if hasattr(result, "content") else str(result)

        print(f"Bot: {bot_reply}")


        # Update conversation history
        context += f"\nYou: {user_input}\nBot: {bot_reply}\n"


if __name__ == "__main__":
    handle_conversation()
