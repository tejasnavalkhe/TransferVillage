from flask import Blueprint, render_template, request
from flask_login import login_required, current_user
from TransferVillage.models import File
from TransferVillage import db
from uuid import uuid4
import os

files = Blueprint('files', __name__)

@files.route('/upload/', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        files = request.files.getlist('files')
        convert = request.form.get('convert')
        is_private = request.form.get('is_private')
        password = request.form.get('password')
        is_expiry = request.form.get('is_expiry')
        expiry_datetime = request.form.get('expiry_datetime')

        # Check for user unique directly if not exists then create.
        if not os.path.isdir(f'TransferVillage/uploads/{current_user.email}/'):
            os.mkdir(f'TransferVillage/uploads/{current_user.email}')

        if len(files) > 1:
            folder_name = str(uuid4()) + '.' + str(current_user.id)
            os.mkdir(f'TransferVillage/uploads/{current_user.email}/{folder_name}')
            for file in files:
                if convert != '0':
                    if convert == 'WORD' and file.filename.endswith('.pdf'):
                        # Convert PDF to WORD
                        pass
                    elif convert == 'PDF' and file.filename.endswith('.docx'):
                        # Convert WORD to PDF
                        pass
                file.save(f"TransferVillage/uploads/{current_user.email}/{folder_name}/{file.filename}")
        elif len(files) == 1:
            if convert != '0':
                if convert == 'WORD' and files[0].filename.endswith('.pdf'):
                    # Convert PDF to WORD
                    pass
                elif convert == 'PDF' and files[0].filename.endswith('.docx'):
                    # Convert WORD to PDF
                    pass
            files[0].save(f"TransferVillage/uploads/{current_user.email}/{files[0].filename}")
    return render_template('share/file.html')

@files.route('/share/<unique_code>/', methods=['GET', 'POST'])
def share(unique_code):
    return render_template('share/file.html')
