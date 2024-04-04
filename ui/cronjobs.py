#Cron jobs
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