from pathlib import Path
import os
import time
import traceback
from utils import global_const as gc
# from utils import setup_logger_common  # TODO: figure out how to import setup_logger_common from utils module
from .log_utils import * #setup_logger_common


def get_project_root():
    # Returns project root folder.
    return Path(__file__).parent.parent

def file_exists(fn):
    try:
        with open(fn, "r"):
            return 1
    except IOError:
        return 0

# validates presence of a single environment variable
def validate_envir_variable(var_name):
    out = False
    if os.environ.get(var_name):
        out = True
    return out

# verifies if the list to_add parameter is a list and extend the target list with its values
def extend_list_with_other_list(list_trg, list_to_add):
    if list_to_add and isinstance(list_to_add, list):
        list_trg.extend(list_to_add)
    return list_trg

def setup_logger(m_cfg, log_dir_location, cur_proc_name_prefix = None):
    # get logging related config values
    common_logger_name = gc.MAIN_LOG_NAME
    log_folder_name = gc.LOG_FOLDER_NAME
    logging_level = m_cfg.get_value('Logging/main_log_level')
    # get current location of the script and create Log folder
    # wrkdir = Path(os.path.dirname(os.path.abspath(__file__))) / log_folder_name  # 'logs'
    wrkdir = Path(log_dir_location) / log_folder_name

    # lg_filename = time.strftime("%Y%m%d_%H%M%S", time.localtime()) + '.log'
    if not cur_proc_name_prefix:
        lg_filename = '{}_{}'.format(time.strftime("%Y%m%d_%H%M%S", time.localtime()),'.log')
    else:
        lg_filename = '{}_{}_{}'.format(cur_proc_name_prefix, time.strftime("%Y%m%d_%H%M%S", time.localtime()), '.log')
    # setup logger

    lg = setup_logger_common(common_logger_name, logging_level, wrkdir, lg_filename)  # logging_level
    #mlog = lg['logger']
    return lg['logger'], lg['handler']

def stop_logger (logger, handler):
    deactivate_logger_common(logger, handler)

def is_binary(file_name):
    try:
        with open(file_name, 'tr') as check_file:  # try open file in text mode
            check_file.read()
            return False
    except:  # if fail then file is non-text (binary)
        return True