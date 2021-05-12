import os, inspect
from pathlib import Path
from utils import global_const as gc
from utils import ConfigData
from utils import common as cm
from flask import request


"""
# not in use
def getConfigAndLogRefs (log_file_name):
    mcfg = get_main_config()
    mlog, mlog_handler = get_logger(log_file_name)
    return mcfg, mlog, mlog_handler
"""

# get main config reference
def get_main_config():
    if not gc.main_cfg:
        gc.main_cfg = ConfigData(gc.MAIN_CONFIG_FILE)
    return gc.main_cfg

# setup logger for the current web request
def get_logger(process_log_id = None):
    if not process_log_id:
        process_log_id = inspect.stack()[1][3]
    # load main config file and get required values
    m_cfg = get_main_config() #ConfigData(gc.MAIN_CONFIG_FILE)

    # setup application level logger
    cur_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    mlog, mlog_handler = cm.setup_logger(m_cfg, cur_dir.parent.absolute(), process_log_id)

    return mlog, mlog_handler

# stop logger
def stop_logger(logger, handler):
    cm.stop_logger(logger, handler)

def clean_log_directory():
    import time

    m_cfg = get_main_config()
    # identify log directory
    cur_dir = Path(os.path.dirname(os.path.abspath(__file__))).parent.absolute()
    log_dir = Path(cur_dir) / gc.LOG_FOLDER_NAME
    # number of days to keep logs
    keep_log_days = m_cfg.get_value('Logging/keep_log_days')
    now = time.time()
    cutoff = now - (int(keep_log_days) * 86400)
    # get list of log files
    files = os.listdir(log_dir)
    # loop through files
    for file in files:
        if file.endswith(".log"):
            file_path = str(Path(str(log_dir) + '/' + file))
            if os.path.isfile(file_path):
                t = os.stat(file_path)
                c = t.st_mtime  # st_ctime - creation time, st_mtime - modification time

                # delete file if older than 10 days
                if c < cutoff:
                    os.remove(file_path)

def check_env_variables(call_from_file, log_ref):
    valid_msg = ''
    if not gc.env_validated:
        # current function: inspect.stack()[0][3], current caller: inspect.stack()[1][3]
        caller = inspect.stack()[1][3]  # current function name
        # cur_file = os.path.realpath(call_from_file)  # current file name
        # validate expected environment variables; if some variable are not present, abort execution
        gc.env_validated, valid_msg = validate_available_envir_variables(log_ref, gc.main_cfg, ['default'],
                                                                 '{}=>{}'.format(call_from_file, caller))
    return gc.env_validated, valid_msg

# Validate expected Environment variables; if some variable are not present, abort execution
# setup environment variable sources:
# windows: https://www.youtube.com/watch?v=IolxqkL7cD8
# linux: https://www.youtube.com/watch?v=5iWhQWVXosU
def validate_available_envir_variables (mlog, m_cfg, env_cfg_groups = None, process_name = None):
    # env_cfg_groups should be a list of config groups of expected environment variables
    if not env_cfg_groups:
        env_cfg_groups = []
    if not isinstance(env_cfg_groups, list):
        env_cfg_groups = [env_cfg_groups]

    app_path_to_report =Path(os.path.abspath(__file__)).parent.absolute()

    if mlog:
        mlog.info('Start validating presence of required environment variables.')
    env_vars = []
    env_var_confs = m_cfg.get_value('Validate/environment_variables')  # get dictionary of envir variables lists
    if env_var_confs and isinstance(env_var_confs, dict):
        for env_gr in env_var_confs:  # loop groups of envir variables
            if env_gr in env_cfg_groups:
                # proceed here for the "default" group of envir variables
                env_vars = cm.extend_list_with_other_list(env_vars, env_var_confs[env_gr])
        # validate existence of the environment variables
        missing_env_vars = []
        for evar in env_vars:
            if not cm.validate_envir_variable(evar):
                missing_env_vars.append(evar)

        if missing_env_vars:
            # check if any environment variables were recorded as missing
            _str = 'Process: {}. The following environment variables were not found: {}.'\
                .format(process_name if process_name else 'Unknown', missing_env_vars)
            if mlog:
                mlog.error(_str)

            # # TODO: decide if sending email is needed
            # # send notification email alerting about the error case
            # email_subject = m_cfg.get_value('Email/email_subject')
            # email_body = 'Application: {}\nError message: {}'\
            #     .format(m_cfg.get_value('Email/application_id'), _str)
            # try:
            #     email.send_yagmail(
            #         emails_to=m_cfg.get_value('Email/sent_to_emails'),
            #         subject=email_subject,
            #         message=email_body
            #         # ,attachment_path = email_attchms_study
            #     )
            # except Exception as ex:
            #     # report unexpected error during sending emails to a log file and continue
            #     _str = 'Unexpected Error "{}" occurred during an attempt to send an email.\n{}'.\
            #         format(ex, traceback.format_exc())
            #     if mlog:
            #         mlog.critical(_str)

            return False, _str
        else:
            if mlog:
                mlog.info('Process: {}. All required environment variables were found.'
                      .format(process_name if process_name else 'Unknown'))
            return True, ''

# get client ip based on the current request
def get_client_ip():
    if request.environ.get('HTTP_X_FORWARDED_FOR') is None:
        return request.environ['REMOTE_ADDR']
    else:
        return request.environ['HTTP_X_FORWARDED_FOR']  # if behind a proxy