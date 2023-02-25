from TransferVillage import mail
from flask_mail import Message
from flask import url_for, current_app

def send_confirm_email(email, token):
    msg = Message('Confirm Your Account',
                  sender=('TEJEarning', 'support@tejearning.com'), recipients=[email])
    msg.body = f'''To confirm your email, visit the following link. The link will expire in 10 minutes:
{url_for('main.confirm_email', token=token, _external=True)}

'''
    mail.send(msg)


def new_user(fname, lname, email, mobile):
    msg = Message('New User Registered', sender=('TEJEarning', 'support@tejearning.com'),
                  recipients=['support@tejearning.com'])
    msg.body = f'''Name: {fname} {lname}
Email: {email}
Mobile Number: {mobile}
'''
    mail.send(msg)


def send_reset_email(user):
    token = user.get_reset_token()
    print(url_for('main.reset_token', token=token, _external=True))
    msg = Message('Password Reset Request',
                  sender=('TEJEarning', 'support@tejearning.com'), recipients=[user.email])
    msg.body = f'''To reset your password, visit the following link. The link will expire in 10 minutes:
{url_for('main.reset_token', token=token, _external=True)}

If your did not make this request then simply ignore this email and no changes will be made.
'''
    mail.send(msg)
