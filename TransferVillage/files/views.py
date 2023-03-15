from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from TransferVillage.models import File
from TransferVillage import db
from TransferVillage.files.utils import BOTO_S3, FileHandler
from uuid import uuid4
from datetime import datetime, timedelta
import os
import pytz

files = Blueprint('files', __name__)
tz = pytz.timezone('Asia/Calcutta')
s3 = BOTO_S3()
file_handler = FileHandler()

@files.route('/upload/', methods=['GET', 'POST'])
@login_required
def upload():
    if request.method == 'POST':
        files = request.files.getlist('files')
        convert = request.form.get('convert')
        is_private = request.form.get('is_private')
        is_expiry = request.form.get('is_expiry')

        # Password
        if is_private == 'on':
            is_private = True
            if not request.form.get('password'):
                password = str(uuid4())[0:8:]
            else:
                password = request.form.get('password')
        else:
            is_private = False
            password = None

        # Expiry
        if is_expiry == 'on':
            is_expiry = True
            expiry_datetime = request.form.get('expiry_datetime')
            if expiry_datetime:
                expiry_datetime_obj = datetime.strptime(expiry_datetime, '%Y-%m-%dT%H:%M')
            else:
                expiry_datetime_obj = str(datetime.now(tz) + timedelta(days=7))
                expiry_datetime_obj = expiry_datetime_obj.split('.')[0]
                expiry_datetime_obj = datetime.strptime(expiry_datetime_obj, '%Y-%m-%d %H:%M:%S')
        else:
            is_expiry = False
            expiry_datetime_obj = None

        # Check for user unique folder if not exists then create.
        if not os.path.isdir(f'TransferVillage/uploads/{current_user.id}/'):
            os.mkdir(f'TransferVillage/uploads/{current_user.id}')

        if len(files) > 1:
            folder_name = str(uuid4()) + '.' + str(current_user.id)
            files_not_allowed = []
            for file in files:
                exten_rslt = file_handler.allowed_file(file.filename)
                unique_filename = str(uuid4())+'.'+file.filename.rsplit('.', 1)[1]
                original_filename = file.filename
                if not exten_rslt:
                    files_not_allowed.append(file.filename)
                    continue
                if convert != '0':
                    file.save(f'TransferVillage/uploads/{current_user.id}/{file.filename}')
                    if convert == 'WORD' and (not file.filename.endswith('.docx')):
                        if file.filename.endswith('.pdf'):
                            file_handler.PDF_TO_WORD(f'TransferVillage/uploads/{current_user.id}/{file.filename}')
                        elif file.filename.endswith('.txt'):
                            with open(f'TransferVillage/uploads/{current_user.id}/{file.filename}', "r") as file_obj:
                                doc = file_handler.TXT_TO_WORD(file_obj)
                                doc.save(f'TransferVillage/uploads/{current_user.id}/{file.filename.rsplit(".", 1)[0]}.docx')
                        os.remove(f'TransferVillage/uploads/{current_user.id}/{file.filename}')
                        with open(f'TransferVillage/uploads/{current_user.id}/{file.filename.rsplit(".", 1)[0]}.docx', 'rb') as new_file:
                            result = s3.upload_file(new_file, unique_filename.rsplit('.', 1)[0]+'.docx', folder_name)
                            if result:
                                unique_id = str(uuid4())
                                _file = File(id=unique_id, folder_name=folder_name, original_filename=original_filename, filename=unique_filename.rsplit('.', 1)[0]+'.docx', is_private=is_private, password=password, is_expiry=is_expiry, expires_at=expiry_datetime_obj, uploaded_at=datetime.now(tz), link=url_for('files.share_file', filename=unique_filename.rsplit('.', 1)[0]+'.docx', _external=True), user_id=current_user.id)
                                db.session.add(_file)
                                db.session.commit()
                                os.remove(f'TransferVillage/uploads/{current_user.id}/{file.filename.rsplit(".", 1)[0]}.docx')
                    elif convert == 'PDF' and (not file.filename.endswith('.pdf')):
                        if file.filename.endswith('.docx'):
                            file_handler.WORD_TO_PDF(f'TransferVillage/uploads/{current_user.id}/{file.filename}')
                        elif file.filename.endswith('.txt'):
                            with open(f'TransferVillage/uploads/{current_user.id}/{file.filename}', "r") as file_obj:
                                pdf = file_handler.TXT_TO_PDF(file_obj)
                                pdf.output(f'TransferVillage/uploads/{current_user.id}/{file.filename.rsplit(".", 1)[0]}.pdf')
                        elif (file.filename.endswith('.png') or file.filename.endswith('.jpeg') or file.filename.endswith('.jpg')):
                            file_handler.IMAGE_TO_PDF(f'TransferVillage/uploads/{current_user.id}/{file.filename}', f'TransferVillage/uploads/{current_user.id}/{file.filename.rsplit(".", 1)[0]}.pdf')
                        elif file.filename.endswith('.xlsx'):
                            pdf = file_handler.EXCEL_TO_PDF(f'TransferVillage/uploads/{current_user.id}/{file.filename}')
                            pdf.output(f'TransferVillage/uploads/{current_user.id}/{file.filename.rsplit(".", 1)[0]}.pdf')
                        os.remove(f'TransferVillage/uploads/{current_user.id}/{file.filename}')
                        with open(f'TransferVillage/uploads/{current_user.id}/{file.filename.rsplit(".", 1)[0]}.pdf', 'rb') as new_file:
                            result = s3.upload_file(new_file, unique_filename.rsplit('.', 1)[0]+'.pdf', folder_name)
                            if result:
                                unique_id = str(uuid4())
                                _file = File(id=unique_id, folder_name=folder_name, original_filename=original_filename, filename=unique_filename.rsplit('.', 1)[0]+'.pdf', is_private=is_private, password=password, is_expiry=is_expiry, expires_at=expiry_datetime_obj, uploaded_at=datetime.now(tz), link=url_for('files.share_file', filename=unique_filename.rsplit('.', 1)[0]+'.pdf', _external=True), user_id=current_user.id)
                                db.session.add(_file)
                                db.session.commit()
                                os.remove(f'TransferVillage/uploads/{current_user.id}/{file.filename.rsplit(".", 1)[0]}.pdf')
                    else:
                        result = s3.upload_file(file, unique_filename, folder_name)
                        if result:
                            unique_id = str(uuid4())
                            _file = File(id=unique_id, folder_name=folder_name, original_filename=original_filename, filename=unique_filename, is_private=is_private, password=password, is_expiry=is_expiry, expires_at=expiry_datetime_obj, uploaded_at=datetime.now(tz), link=url_for('files.share_file', filename=unique_filename, _external=True), user_id=current_user.id)
                            db.session.add(_file)
                            db.session.commit()
                else:
                    result = s3.upload_file(file, unique_filename, folder_name)
                    if result:
                        unique_id = str(uuid4())
                        _file = File(id=unique_id, folder_name=folder_name, original_filename=original_filename, filename=unique_filename, is_private=is_private, password=password, is_expiry=is_expiry, expires_at=expiry_datetime_obj, uploaded_at=datetime.now(tz), link=url_for('files.share_file', filename=unique_filename, _external=True), user_id=current_user.id)
                        db.session.add(_file)
                        db.session.commit()
            if len(files_not_allowed) > 0:
                flash(f"Some files are not allowed to be uploaded because of the extension. File(s) is(are) {', '.join(files_not_allowed)}", "danger")
            else:
                flash("Files uploaded successfully.", "success")
            return redirect(url_for('main.dashboard'))
        elif len(files) == 1:
            exten_rslt = file_handler.allowed_file(files[0].filename)
            unique_filename = str(uuid4())+'.'+files[0].filename.rsplit('.', 1)[1]
            original_filename = files[0].filename
            if not exten_rslt:
                flash(f"The file is not allowed to be uploaded because of the extension. File is {files[0].filename}", "danger")
                return redirect(url_for('main.dashboard'))
            if convert != '0':
                files[0].save(f'TransferVillage/uploads/{current_user.id}/{files[0].filename}')
                if convert == 'WORD' and (not files[0].filename.endswith('.docx')):
                    if files[0].filename.endswith('.pdf'):
                        file_handler.PDF_TO_WORD(f'TransferVillage/uploads/{current_user.id}/{files[0].filename}')
                    elif files[0].filename.endswith('.txt'):
                        with open(f'TransferVillage/uploads/{current_user.id}/{files[0].filename}', "r") as file_obj:
                            doc = file_handler.TXT_TO_WORD(file_obj)
                            doc.save(f'TransferVillage/uploads/{current_user.id}/{files[0].filename.rsplit(".", 1)[0]}.docx')
                    os.remove(f'TransferVillage/uploads/{current_user.id}/{files[0].filename}')
                    with open(f'TransferVillage/uploads/{current_user.id}/{files[0].filename.rsplit(".", 1)[0]}.docx', 'rb') as new_file:
                        result = s3.upload_file(new_file, unique_filename.rsplit('.', 1)[0]+'.docx')
                        if result:
                            unique_id = str(uuid4())
                            _file = File(id=unique_id, folder_name=None, original_filename=original_filename, filename=unique_filename.rsplit('.', 1)[0]+'.docx', is_private=is_private, password=password, is_expiry=is_expiry, expires_at=expiry_datetime_obj, uploaded_at=datetime.now(tz), link=url_for('files.share_file', filename=unique_filename.rsplit('.', 1)[0]+'.docx', _external=True), user_id=current_user.id)
                            db.session.add(_file)
                            db.session.commit()
                            os.remove(f'TransferVillage/uploads/{current_user.id}/{files[0].filename.rsplit(".", 1)[0]}.docx')
                elif convert == 'PDF' and (not files[0].filename.endswith('.pdf')):
                    if files[0].filename.endswith('.docx'):
                        file_handler.WORD_TO_PDF(f'TransferVillage/uploads/{current_user.id}/{files[0].filename}')
                    elif files[0].filename.endswith('.txt'):
                        with open(f'TransferVillage/uploads/{current_user.id}/{files[0].filename}', "r") as file_obj:
                            pdf = file_handler.TXT_TO_PDF(file_obj)
                            pdf.output(f'TransferVillage/uploads/{current_user.id}/{files[0].filename.rsplit(".", 1)[0]}.pdf')
                    elif (files[0].filename.endswith('.png') or files[0].filename.endswith('.jpeg') or files[0].filename.endswith('.jpg')):
                        file_handler.IMAGE_TO_PDF(f'TransferVillage/uploads/{current_user.id}/{files[0].filename}', f'TransferVillage/uploads/{current_user.id}/{files[0].filename.rsplit(".", 1)[0]}.pdf')
                    elif files[0].filename.endswith('.xlsx'):
                        pdf = file_handler.EXCEL_TO_PDF(f'TransferVillage/uploads/{current_user.id}/{files[0].filename}')
                        pdf.output(f'TransferVillage/uploads/{current_user.id}/{files[0].filename.rsplit(".", 1)[0]}.pdf')
                    os.remove(f'TransferVillage/uploads/{current_user.id}/{files[0].filename}')
                    with open(f'TransferVillage/uploads/{current_user.id}/{files[0].filename.rsplit(".", 1)[0]}.pdf', 'rb') as new_file:
                        result = s3.upload_file(new_file, unique_filename.rsplit('.', 1)[0]+'.pdf')
                        if result:
                            unique_id = str(uuid4())
                            _file = File(id=unique_id, folder_name=None, original_filename=original_filename, filename=unique_filename.rsplit('.', 1)[0]+'.pdf', is_private=is_private, password=password, is_expiry=is_expiry, expires_at=expiry_datetime_obj, uploaded_at=datetime.now(tz), link=url_for('files.share_file', filename=unique_filename.rsplit('.', 1)[0]+'.pdf', _external=True), user_id=current_user.id)
                            db.session.add(_file)
                            db.session.commit()
                            os.remove(f'TransferVillage/uploads/{current_user.id}/{files[0].filename.rsplit(".", 1)[0]}.pdf')
                else:
                    unique_filename = str(uuid4())+'.'+files[0].filename.rsplit('.', 1)[1]
                    result = s3.upload_file(files[0], unique_filename)
                    if result:
                        unique_id = str(uuid4())
                        _file = File(id=unique_id, folder_name=None, original_filename=original_filename, filename=unique_filename, is_private=is_private, password=password, is_expiry=is_expiry, expires_at=expiry_datetime_obj, uploaded_at=datetime.now(tz), link=url_for('files.share_file', filename=unique_filename, _external=True), user_id=current_user.id)
                        db.session.add(_file)
                        db.session.commit()
            else:
                unique_filename = str(uuid4())+'.'+files[0].filename.rsplit('.', 1)[1]
                result = s3.upload_file(files[0], unique_filename)
                if result:
                    unique_id = str(uuid4())
                    _file = File(id=unique_id, folder_name=None, original_filename=original_filename, filename=unique_filename, is_private=is_private, password=password, is_expiry=is_expiry, expires_at=expiry_datetime_obj, uploaded_at=datetime.now(tz), link=url_for('files.share_file', filename=unique_filename, _external=True), user_id=current_user.id)
                    db.session.add(_file)
                    db.session.commit()
            flash("Files uploaded successfully.", "success")
            return redirect(url_for('main.dashboard'))
    return render_template('share/file.html')

@files.route('/share/<filename>/', methods=['GET', 'POST'])
def share_file(filename):
    if request.method == 'POST':
        file_ = File.query.filter_by(filename=filename).first()
        if request.form.get('password') == file_.password:
            if file_.folder_name:
                url = s3.create_presigned_url(f"{file_.folder_name}/{file_.filename}")
            else:
                url = s3.create_presigned_url(file_.filename)
            return redirect(url)
        else:
            flash("Either you entered wrong password or password has been changed by the owner.", "danger")
            return redirect(url_for('main.home'))
    file_ = File.query.filter_by(filename=filename).first()
    if file_.is_private:
        return render_template('share/password.html', filename=file_.filename)
    else:
        if file_.folder_name:
            url = s3.create_presigned_url(f"{file_.folder_name}/{file_.filename}")
        else:
            url = s3.create_presigned_url(file_.filename)
        return redirect(url)
