from flask import (
    Blueprint,
    render_template,
    request,
    flash
)
import yaml
from flask_login import login_required
from crontab import CronTab

#wrap file and cron with try excepts unless flash deals with that


job_scheduling = Blueprint("job_scheduling", __name__)

@job_scheduling.route("", methods=["GET"])
@login_required
def load_page():
    return render_template("job_scheduling.html")


cron_job_file = "./cronjobtest.yaml"

@job_scheduling.route("", methods=["POST"])
@login_required
def change_schedule():
    day_to_cron_map = {
        "SUN": "0",
        "MON": "1",
        "TUE": "2",
        "WED": "3",
        "THU": "4",
        "FRI": "5",
        "SAT": "6",
    }

    #get the cron file
    with open(cron_job_file, 'r') as cronfile:
        cron_jobs = yaml.safe_load(cronfile)
    
    #THIS NEED TO BE CHANGED WHEN THE TEMPLATE IS UPDATED
    job_script_name = request.form['jobType']
    time = request.form['time'] #change this to many variables and combined them into a a single cron format variable.
    day_of_week_start = day_to_cron_map.get(request.form.get('dayOfWeekStart', ''))
    day_of_week_end = day_to_cron_map.get(request.form.get('dayOfWeekEnd', ''))
    day_of_month = request.form.getlist('dayOfMonth')

    if day_of_month != '*':
        day_of_month = ','.join(day_of_month) 
        #this spits out a comma separated list of values if multiple days are selected
        #if only one day is selected it will still work
        day_of_week_cron = '*'
        #if day of month is selected in the form then override day of week and make it a *
    else:
        day_of_month = '*' #set day of month to be * if non was selected
        if day_of_week_start <= day_of_week_end:
            # Direct sequence (e.g., Monday to Friday)
            day_sequence = [str(day) for day in range(int(day_of_week_start), int(day_of_week_end) + 1)]
        else:
            # Wrap-around sequence (e.g., Friday to Tuesday)
            day_sequence = [str(day) for day in range(int(day_of_week_start), 7)] + \
                        [str(day) for day in range(0, int(day_of_week_end) + 1)]
        day_of_week_cron = ','.join(day_sequence)
        #add commas in between day numbers for cron format
    

    hour, minute = time.split(':') if time else ('*','*') #if time isnt selected then set it to * in hour and min

    cron_time_input = f"{minute} {hour} {day_of_month} * {day_of_week_cron}"

    if job_script_name in cron_jobs: #if the cron jobs file has a setting for the selected data collection job
        cron_jobs[job_script_name]['time'] = cron_time_input   #set the cron job time to be what the front end sends us... THIS NEEDS TO BE CHANGED WITH THE UPDATED FRONTEND
        script_path = cron_jobs[job_script_name]['script_path']
        #get the script path to write to the actual cron jobs later
    else:
        return flash("File not found", category='error') #replace with better error msgs or logging later, also dont think this works

    #write ot the cron file
    with open(cron_job_file, 'w') as cronfile:
        yaml.safe_dump(cron_jobs, cronfile)

    #crontab docs https://pypi.org/project/python-crontab/
    #Update actual cron jobs
    cron = CronTab(user=True)  # Use user=True to manage the current user's crontab
    #Remove existing jobs of the same type as the cron_jobs variable from the cronjobtest file ##CHANGE LATER WHEN UPDATING THE FILE NAME
    cron.remove_all(comment=job_script_name)
    #Create a new job with the updated information
    job = cron.new(command=f'{script_path} >> ~/ATSLogs/cron_log.txt 2>&1', comment=job_script_name)
    job.setall(cron_time_input)
    cron.write()

    return flash("Cron job updated successfully.", category='message') #idk about flash and how to get this to work... -Dom