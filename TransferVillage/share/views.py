from flask import Blueprint, render_template, redirect
from flask_login import login_required

share = Blueprint('share', __name__)

@share.route('/')
@login_required
def file():
    return render_template('')
