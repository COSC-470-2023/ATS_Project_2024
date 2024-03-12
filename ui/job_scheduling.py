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
import yaml
from flask_login import login_required
from crontab import CronTab

job_scheduling = Blueprint("job_scheduling", __name__)

@job_scheduling.route("", methods=["GET"])
@login_required
def load_page():
    return render_template("job_scheduling.html")


cron_job_file = "./"

@job_scheduling.route("", methods=["POST"])
@login_required
def change_schedule():
    with open(cron_job_file, 'r') as cronfile:
        cron_jobs = yaml.safe_load(cronfile)
    
    #THIS NEED TO BE CHANGED WHEN THE TEMPLATE IS UPDATED
    job_script_name = request.form['table-in-question']
    time = request.form['time']

    


    with open(cron_job_file, 'w') as cronfile:
        cron_jobs = yaml.safe_dump(cronfile)

    #crontab docs https://pypi.org/project/python-crontab/
    #Update actual cron jobs
    cron = CronTab(user=True)  # Use user=True to manage the current user's crontab
    #Remove existing jobs of the same type
    cron.remove_all(comment=job_type)
    #Create a new job with the updated information
    job = cron.new(command=f'{script_path} >> ~/ATSLogs/cron_log.txt 2>&1', comment=job_type)
    job.setall(time)
    cron.write()


    return