from flask import (
    Blueprint,
    render_template,
    request,
    flash,
)
import json
from flask_login import login_required
from crontab import CronTab
from .decorators import admin_required

job_scheduling = Blueprint("job_scheduling", __name__)

# It should be noted that The code does not update the job commands ever once they are set.
# Because we should never have to update the commands themselves unless manually and only once.
# It does set the default cron job command to the default upon first load where no cron jobs are found.


@job_scheduling.route("/", methods=["GET"])
@admin_required
def load_page():
    cron = CronTab(user=True)  # Use user=True to manage the current user's crontab
    for job in listOfJobs:
        cronjob = next(cron.find_comment(job["name"]), None)
        if cronjob == None: #if the job doesn't exist currently then use defaults
            cronjob = cron.new(command=job["command"], comment=job["name"])
            cronjob.setall(job["default"])
            cron.write()
        hour = str(cronjob.hour)
        minute = str(cronjob.minute)
        day = str(cronjob.dow)
        month = str(cronjob.dom)
        if hour != "*":
            job["hour"] = int(hour)

        if minute != "*":
            job["minute"] = int(minute)

        if day != "*":
            job["day"] = list(
                map(int, day.split(","))
            )  # make all the multiple days selected into a list of

        if month != "*":
            # month.split(',') commented out for when the day of the month becomes a multiselect
            job["month"] = list(map(int, month.split(",")))

    return render_template("job_scheduling.html", jobschedule=json.dumps(listOfJobs))


#form submission
@job_scheduling.route("/", methods=["POST"])
@admin_required
def change_schedule():
    job_name = request.form["inputJobType"]
    time = request.form[
        "time"
    ]  # change this to many variables and combined them into a a single cron format variable.
    day_of_week = request.form.getlist("dayOfWeek")
    day_of_month = request.form.getlist("dayOfMonth")
    repeat_method = request.form["RepeatMethod"]

    print(repeat_method)

    if repeat_method == "DOM":
        day_of_month = ",".join(day_of_month) if day_of_month else "*"
        # this spits out a comma separated list of values if multiple days are selected
        # if only one day is selected it will still work
        day_of_week = "*"
        # if day of month is selected in the form then override day of week and make it a *
    else:
        day_of_month = "*"  # set day of month to be * if non was selected
        day_of_week = ",".join(day_of_week) if day_of_week else "*"
        # add commas in between day numbers for cron format

    hour, minute = (
        time.split(":") if time else ("*", "0")
    )  # if time isnt selected then set it to * in hour and 0 min it will run every hour be careful

    cron_time_input = f"{minute} {hour} {day_of_month} * {day_of_week}"

    # crontab docs https://pypi.org/project/python-crontab/
    # Update actual cron jobs
    cron = CronTab(user=True)  # Use user=True to manage the current user's crontab
    cronjob = next(cron.find_comment(job_name), None)
    cronjob.setall(cron_time_input)
    cron.write()

    #get the current cron jobs and rerender the template with the updated values.
    for job in listOfJobs:
        cronjob = next(cron.find_comment(job["name"]), None)
        if cronjob == None: #if the job doesn't exist currently then use defaults
            cronjob = cron.new(command=job["command"], comment=job["name"])
            cronjob.setall(job["default"])
            cron.write()
        hour = str(cronjob.hour)
        minute = str(cronjob.minute)
        day = str(cronjob.dow)
        month = str(cronjob.dom)
        if hour != "*":
            job["hour"] = int(hour)

        if minute != "*":
            job["minute"] = int(minute)

        if day != "*":
            job["day"] = list(
                map(int, day.split(","))
            )  # make all the multiple days selected into a list of

        if month != "*":
            job["month"] = list(map(int, month.split(",")))

    return render_template("job_scheduling.html", jobschedule=json.dumps(listOfJobs))



listOfJobs = [
        {
            "name": "SymbolChanges",
            "hour": None,
            "minute": None,
            "day": None,
            "month": None,
            "default": "0 10 * * 1,2,3,4,5",
            "command": "ATS_Project_2024/scripts/symbol_change_scheduling.sh >> ~/ATSLogs/cron_log.txt 2>&1",
        },
        {
            "name": "RealtimeData",
            "hour": None,
            "minute": None,
            "day": None,
            "month": None,
            "default": "0 16 * * 1,2,3,4,5",
            "command": "ATS_Project_2024/scripts/realtime_scheduling.sh >> ~/ATSLogs/cron_log.txt 2>&1",
        },
        {
            "name": "Bonds",
            "hour": None,
            "minute": None,
            "day": None,
            "month": None,
            "default": "0 0 * * 6",
            "command": "ATS_Project_2024/scripts/bond_scheduling.sh >> ~/ATSLogs/cron_log.txt 2>&1",
        },
        {
            "name": "CompanyStatements",
            "hour": None,
            "minute": None,
            "day": None,
            "month": None,
            "default": "0 0 * * 0",
            "command": "ATS_Project_2024/scripts/company_statement_scheduling.sh >> ~/ATSLogs/cron_log.txt 2>&1",
        },
    ]