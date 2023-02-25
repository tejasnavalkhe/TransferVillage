from flask import Blueprint, redirect, url_for, flash, request, render_template, current_app
from flask_login import login_user, logout_user, current_user, login_required
from TransferVillage.models import *
from TransferVillage import db, bcrypt
from TransferVillage.main.utils import *
from datetime import datetime, timedelta
import pytz
from itsdangerous import URLSafeTimedSerializer as URLSerializer
from itsdangerous import SignatureExpired, BadTimeSignature


main = Blueprint('main', __name__)
tz = pytz.timezone("Asia/Calcutta")

@main.route('/')
def home():
    return render_template('main/index.html', home="active")

# ------ Register Route ------ #
@main.route('/register/', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('files.upload'))
    if request.method == 'POST':
        if not User.query.filter_by(email=request.form.get('email').strip().lower()).first():
            s = URLSerializer(current_app.config['SECRET_KEY'])
            token = s.dumps({"email": request.form.get('email').strip().lower(), "fname": request.form.get('fname').strip().title(), "lname": request.form.get('lname').strip().title(), "mobile_number": request.form.get('mobile_number'), "password": request.form.get('password')}, salt="send-email-confirmation")
            try:
                print(token)
                send_confirm_email(email=request.form.get('email').strip().lower(), token=token)
            except Exception as e:
                print(e)
            flash(
                f"An confirmation email has been sent to you on {request.form.get('email').strip().lower()}! Please, click on that link to activate your account. The link will expire in 10 minutes.", "success")
            return redirect(url_for('main.login'))
        else:
            flash("You are already registered. Please login to share files.", "success")
            return redirect(url_for('main.login'))
    return render_template('main/register.html')

# ------ Confirm Registration ------ #
@main.route('/confirm_email/<token>/')
def confirm_email(token):
    s = URLSerializer(current_app.config['SECRET_KEY'])
    try:
        data = s.loads(token, salt="send-email-confirmation", max_age=600)
        user = User(fname=data["fname"], email=data["email"], lname=data["lname"], mobile_number=data["mobile_number"],
                    password=bcrypt.generate_password_hash(data["password"]).decode('utf-8'), created_at=datetime.now(tz), modified_at=datetime.now(tz))
        db.session.add(user)
        db.session.commit()
        new_user(fname=data['fname'], lname=data['lname'], email=data["email"],
                    mobile=data["mobile_number"])
        login_user(user)
        flash("Your account has been created successfully!", "success")
        return redirect(url_for('files.upload'))
    except (SignatureExpired, BadTimeSignature):
        flash("That is an invalid or expired token", "danger")
        return redirect(url_for('main.register'))

# ------ Login Route ------ #
@main.route('/login/', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('files.upload'))
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form.get('email').strip().lower()).first()
        if user:
            if bcrypt.check_password_hash(user.password, request.form.get('password')):
                login_user(user, remember=True if request.form.get('remember_me') == 'on' else False,
                            duration=timedelta(weeks=1))
                next_page = request.args.get('next')
                flash("User logged in successfully!", "success")
                return redirect(next_page) if next_page else redirect(url_for('main.dashboard'))
            else:
                flash("Please check you password. Password don't match!", "danger")
                return redirect(url_for('main.login'))
        else:
            flash(
                "You don't have an account. Please create now to login.", "danger")
            return redirect(url_for('main.register'))
    return render_template('main/login.html', page='login')

# ------ Logout Route ------ #
@main.route('/logout/')
@login_required
def logout():
    logout_user()
    flash("User has been logged out.", "success")
    return redirect(url_for('main.home'))

# ------ Reset Password Request Route ------ #
@main.route('/reset_password/', methods=['GET', 'POST'])
def reset_request():
    if current_user.is_authenticated:
        return redirect(url_for('files.upload'))
    if request.method == 'POST':
        user = User.query.filter_by(email=request.form.get('email').strip().lower()).first()
        if user:
            send_reset_email(user)
            flash("An email has been sent with instructions to reset your password.", "success")
        else:
            flash("User not found!", "danger")
        return redirect(url_for('main.login'))
    return render_template('main/reset_request.html')

# ------ Reset Password <TOKEN> Route ------ #
@main.route('/reset_password/<token>/', methods=['GET', 'POST'])
def reset_token(token):
    if current_user.is_authenticated:
        return redirect(url_for('files.upload'))
    user = User.verify_reset_token(token)
    if user is None:
        flash("That is an invalid or expired token", "danger")
        return redirect(url_for('main.reset_request'))
    if request.method == 'POST':
        if request.form.get('password') == request.form.get('cpassword'):
            user.password = bcrypt.generate_password_hash(request.form.get('password')).decode('utf-8')
            db.session.commit()
            flash("Your password has been updated! You are now able to login", "success")
            return redirect(url_for('main.login'))
        else:
            flash("Password and confirm password must match.", "danger")
            return redirect(url_for('main.reset_token', token=token))
    return render_template('main/reset_token.html', token=token)

@main.route('/newsletter/', methods=['POST'])
def newsletter():
    email = request.form.get('email')
    if email is None:
        flash("Please enter your email address.", "danger")
        return redirect(url_for('main.home'))

    email = email.strip().lower()
    if not Newsletter.query.filter_by(email=email).first():
        new_newsletter = Newsletter(email=email, created_at=datetime.now(tz))
        db.session.add(new_newsletter)
        db.session.commit()
        flash("Successfully subscribed to newsletter.", "success")
        return redirect(url_for('main.home'))
    else:
        flash("You have already subscribed to newsletter.", "success")
        return redirect(url_for('main.home'))

@main.route('/dashboard/', methods=['GET','POST'])
@login_required
def dashboard():
    files = File.query.filter_by(user_id=current_user.id).all()
    return render_template('main/dashboard.html', dashboard="active", files=files)

@main.route('/settings/', methods=['GET','POST'])
@login_required
def settings():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        cpassword = request.form.get('cpassword')
        if bcrypt.check_password_hash(current_user.password, current_password):
            if new_password == cpassword:
                current_user.password = bcrypt.generate_password_hash(new_password)
                db.session.commit()
                logout_user()
                flash("Password changed successfully.", "success")
                return redirect(url_for('main.login'))
            else:
                flash("Password and confirm password does not match.", "danger")
                return redirect(url_for('main.settings'))
        else:
            flash("Current password does not match.", "danger")
            return redirect(url_for('main.settings'))
    return render_template('main/settings.html', settings="active")
