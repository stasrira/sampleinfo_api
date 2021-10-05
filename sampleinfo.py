from app import app
from os import environ, path
from dotenv import load_dotenv
from flask_apscheduler import APScheduler
from utils import common2 as cm2
from utils import global_const as gc


# load environment variables from files
basedir = path.abspath(path.dirname(__file__))
load_dotenv(path.join(basedir, '.flaskenv'))
load_dotenv(path.join(basedir, '.env'))

# set configuration values to be passed to Flask
class Scheduler_Config:
    SCHEDULER_API_ENABLED = True  # enables calls to the scheduler api, i.e. [server name]/scheduler/jobs

# function to handle scheduler's calls
def scheduler_clean_log_files():
    from utils import common2 as cm2
    cm2.clean_log_directory()

if __name__ == "__main__":
    # load_dotenv('.flaskenv')

    # get host and port for running flask
    host = environ.get('FLASK_RUN_HOST')
    port = environ.get('FLASK_RUN_PORT')
    # test = environ.get('ST_DB_USER_NAME')

    # get reference for the main config file
    mcfg = cm2.get_main_config()
    # get a config value defining if the custom logging should be used
    custom_logging = mcfg.get_value('Logging/custom_logging')
    if isinstance(custom_logging, bool):
        gc.custom_logging = custom_logging
    else:
        # assign False as a default
        gc.custom_logging = False

    app.config.from_object(Scheduler_Config())

    #define and start scheduler
    scheduler = APScheduler()
    scheduler.init_app(app)
    scheduler.add_job(id='scheduler_clean_log_files', func=scheduler_clean_log_files, trigger="interval",
                      seconds=43200)  # 1 day: 86400
    scheduler.start()

    # run the Flask app
    app.run(host=host, port=port, load_dotenv=True)  #host=host, port=port, load_dotenv=True
