from flask import Blueprint, render_template, redirect, url_for
from flask_login import login_required, current_user

views = Blueprint('views', __name__)

@views.route('/')
def home():
    return redirect(url_for('views.login'))

@views.route('/login')
def login():
    return render_template('login.html')

@views.route('/configuration')
@login_required
def configuration():
    return render_template('change_configuration.html')

@views.route('/job-scheduling')
@login_required
def job_scheduling():
    return render_template('job_scheduling.html')

@views.route('/data-export')
@login_required
def data_export():
    return render_template('download_data.html')



