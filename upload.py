import os
import threading
from flask import Flask, render_template
from flask_wtf import FlaskForm
from wtforms import FileField, SubmitField
from wtforms.validators import InputRequired
from werkzeug.utils import secure_filename


import read       # extract_text_from_pdf
import chat       # handle_conversation

app = Flask(__name__)
app.config['SECRET_KEY'] = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = 'pdf'


class UploadFileForm(FlaskForm):
    file = FileField("File", validators=[InputRequired()])
    submit = SubmitField("Upload File")


@app.route('/', methods=['GET', 'POST'])
def upload_file():
    form = UploadFileForm()
    if form.validate_on_submit():
        file = form.file.data

        # build and save the file path
        file_path = os.path.join(
            os.path.abspath(os.path.dirname(__file__)),
            app.config['UPLOAD_FOLDER'],
            secure_filename(file.filename)
        )
        file.save(file_path)

        # Step 1: extract text
        read.extract_text_from_pdf(file_path)

        # Step 2: launch chatbot (non-blocking so Flask response works)
        threading.Thread(
            target=chat.handle_conversation,
            daemon=True
        ).start()

        return " File uploaded, text extracted, and chatbot started in terminal."

    return render_template('index.html', form=form)
