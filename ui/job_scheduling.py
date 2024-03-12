from flask import (
    Blueprint,
    render_template,
    request,
    redirect,
    url_for,
    send_file,
    jsonify,
    session,
)
from flask_login import login_required

job_scheduling = Blueprint("job_scheduling", __name__)

@job_scheduling.route("", methods=["GET"])
@login_required
def load_page():
    return render_template("job_scheduling.html")

@job_scheduling.route("", methods=["POST"])
@login_required
def change_schedule():
    
