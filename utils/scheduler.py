from utils import common2 as cm2
from app import app
from flask_apscheduler import APScheduler

# set configuration values to be passed to Flask
class Scheduler_Config:
    SCHEDULER_API_ENABLED = True  # enables calls to the scheduler api, i.e. [server name]/scheduler/jobs

# function to handle scheduler's calls
def scheduler_clean_log_files():
    cm2.clean_log_directory()

def init_scheduler():
    app.config.from_object(Scheduler_Config())

    # define and start scheduler
    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.add_job(id='scheduler_clean_log_files', func=scheduler_clean_log_files, trigger="interval",
                      seconds=43200)  # 1 day: 86400
    scheduler.start()