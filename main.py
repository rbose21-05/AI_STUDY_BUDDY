import os
from flask import Flask, render_template, request, jsonify
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from wtforms.validators import InputRequired
from werkzeug.utils import secure_filename
from flask_cors import CORS

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate

import read  # contains extract_text_from_pdf

# --- Flask setup ---
app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = 'pdf'

# Ensure upload folder exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# --- Chat setup ---
template = """ 
You are a helpful, friendly AI assistant. 
Always give clear, detailed answers to the user's questions.
If you are unsure, try to give a thoughtful guess rather than refusing.
You are a friendly tutor.

The user will upload a PDF file from where you will receive the text. 
You have to analyze it and prepare a study plan as asked.

Here is the conversation history so far:
{context}

Question: {question}

Answer:
"""

model = ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",   # or "gemini-1.5-pro"
    google_api_key=os.getenv("GOOGLE_API_KEY")
)

prompt = ChatPromptTemplate.from_template(template)
chain = prompt | model

# --- Flask-WTF form ---
class UploadFileForm(FlaskForm):
    file = FileField("File", validators=[InputRequired()])
    submit = SubmitField("Upload File")

# --- Store conversation context globally ---
conversation_context = ""

# --- Routes ---
@app.route("/", methods=["GET", "POST"])
def upload_file():
    global conversation_context
    form = UploadFileForm()
    if form.validate_on_submit():
        file = form.file.data
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Extract PDF text and save to study_guide.txt
        read.extract_text_from_pdf(file_path)

        # Load extracted text into conversation context
        try:
            with open("study_guide.txt", "r", encoding="utf-8") as f:
                conversation_context = f.read()
        except FileNotFoundError:
            conversation_context = ""

        return "File uploaded and text extracted! You can now chat with the bot via /chat endpoint."

    return render_template("index.html", form=form)

@app.route("/chat", methods=["POST"])
def chat():
    """Receive a JSON request: { "message": "..." } and return bot reply."""
    global conversation_context
    data = request.json
    user_message = data.get("message", "")

    if not user_message:
        return jsonify({"error": "No message provided"}), 400

    try:
        result = chain.invoke({
            "context": conversation_context,
            "question": user_message
        })
        bot_reply = getattr(result, "content", str(result))

        # Update conversation context
        conversation_context += f"\nYou: {user_message}\nBot: {bot_reply}\n"

        return jsonify({"reply": bot_reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- Run the app ---
if __name__ == "__main__":
    app.run(debug=True)
