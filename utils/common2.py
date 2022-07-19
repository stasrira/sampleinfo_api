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

# get main config reference
def get_webreports_config():
    if not gc.webreps_cfg:
        gc.webreps_cfg = ConfigData(gc.WEBREPORTS_CONFIG_FILE)
    return gc.webreps_cfg

# setup logger for the current web request
def get_logger(process_log_id = None):
    if gc.custom_logging:
        # if custom logging is allowed, create a log file
        if not process_log_id:
            process_log_id = inspect.stack()[1][3]
        # load main config file and get required values
        m_cfg = get_main_config() #ConfigData(gc.MAIN_CONFIG_FILE)

        # setup application level logger
        cur_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        mlog, mlog_handler = cm.setup_logger(m_cfg, cur_dir.parent.absolute(), process_log_id)
    else:
        # if custom logging is not allowed, set log variables to None
        mlog = None
        mlog_handler = None

    return mlog, mlog_handler

# stop logger
def stop_logger(logger, handler):
    cm.stop_logger(logger, handler)

def clean_log_directory():
    import time
    # from datetime import datetime

    # print ('Starting clean_log_directory, {}'.format(datetime.now().strftime("%d/%m/%Y %H:%M:%S")))

    m_cfg = get_main_config()
    mlog, mlog_handler = get_logger('logger_cleaner')
    mlog.info("Starting log directory cleanup.")

    # identify log directory
    cur_dir = Path(os.path.dirname(os.path.abspath(__file__))).parent.absolute()
    log_dir = Path(cur_dir) / gc.LOG_FOLDER_NAME
    # number of days to keep logs
    keep_log_days = m_cfg.get_value('Logging/keep_log_days')
    now = time.time()
    cutoff = now - (int(keep_log_days) * 86400)
    mlog.info("Current setting for number of days to keep log files: {}".format(keep_log_days))
    mlog.info("Current cutoff date/time for deletion of the log files: {}".format(cutoff))
    # get list of log files
    files = os.listdir(log_dir)
    # loop through files
    for file in files:
        if file.endswith(".log"):
            file_path = str(Path(str(log_dir) + '/' + file))
            mlog.info("Checking file {}, full path: {}".format(file, file_path))
            if os.path.isfile(file_path):
                t = os.stat(file_path)
                c = t.st_mtime  # st_ctime - creation time, st_mtime - modification time
                mlog.info("Current file's date/time stamp: {}".format(c))
                # delete file if older than 10 days
                if c < cutoff:
                    os.remove(file_path)
                    mlog.info("The file {} was recognized as older than the cutoff point and was deleted.".format(file))
    mlog.info("Log directory clean was completed.")
    stop_logger(mlog, mlog_handler)

def check_env_variables(call_from_file, log_ref = None):
    valid_msg = ''
    if not gc.env_validated:
        mlog = None
        mlog_handler = None
        if not log_ref:
            # if logger object was not provided, open a new log
            mlog, mlog_handler = get_logger(get_client_ip())
        # current function: inspect.stack()[0][3], current caller: inspect.stack()[1][3]
        caller = inspect.stack()[1][3]  # current function name
        # cur_file = os.path.realpath(call_from_file)  # current file name
        # validate expected environment variables; if some variable are not present, abort execution
        gc.env_validated, valid_msg = validate_available_envir_variables(
            mlog if not log_ref else log_ref,
            gc.main_cfg, ['default'],
            '{}=>{}'.format(call_from_file, caller)
        )
        if mlog and mlog_handler:
            # close logging if it was open inside this function
            stop_logger(mlog, mlog_handler)
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

def validate_user_existence(user):
    from utils import LdapConnect

    user_exists = False

    mlog, mlog_handler = get_logger(get_client_ip())
    ldc = LdapConnect(mlog)
    if ldc.connected:
        if ldc.validate_user_existence(user):
            user_exists = True

    if mlog and mlog_handler:
        # close logging if it was open inside this function
        stop_logger(mlog, mlog_handler)

    return user_exists

def validate_user_login(user, pwd):
    from utils import LdapConnect

    member_of = os.environ.get('ST_LDAP_USER_MEMBER_OF')

    mlog, mlog_handler = get_logger(get_client_ip())
    ldc = LdapConnect(mlog)
    if mlog and mlog_handler:
        # close logging if it was open inside this function
        stop_logger(mlog, mlog_handler)
    if ldc.connected:
        user_valid, error_str = ldc.validate_user_credentials_by_email(user, pwd)
        if user_valid:
            # valid credentials
            if ldc.validate_member_of_assignment(user, member_of):
                # valid group assignment
                return True, None
            else:
                # wrong group assignment
                return False, 'No rights to view data'
        else:
            # wrong credentials
            return False, 'Wrong credentials'

