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

    mcfg = cm2.get_main_config()
    interval_day = mcfg.get_value('Logging/clean_log_frequency_days')
    if isinstance(interval_day, int) or isinstance(interval_day, float):
        interval_sec = 86400 * interval_day  # assign number of days as per config file
    else:
        interval_sec = 86400  # assign 1 day as default

    # define and start scheduler
    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.add_job(id='scheduler_clean_log_files', func=scheduler_clean_log_files, trigger="interval",
                      seconds=interval_sec)  # 1 day: 86400
    scheduler.start()