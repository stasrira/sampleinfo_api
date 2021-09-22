import pyodbc
import traceback
# from .configuration import ConfigData
from utils import global_const as gc, common2 as cm2
import os


class MetadataDB:

    # CFG_DB_CONN = 'DB/mdb_conn_str'  # name of the config parameter storing DB connection string
    # CFG_DB_SQL_PROC = 'DB/mdb_sql_proc_load_sample'  # name of the config parameter storing DB name of the stored proc
    # CFG_DB_STUDY_ID = 'DB/mdb_study_id'  # name of the config parameter storing value of the MDB study id
    # CFG_DICT_PATH = 'DB/dict_tmpl_fields_node' # name of the config parameter storing value of dictionary path
    # to list of fields
    # CFG_DB_ALLOW_DICT_UPDATE = 'DB/mdb_allow_dict_update'  # name of the config parameter storing values
    # for "allow dict updates"
    # CFG_DB_ALLOW_SAMPLE_UPDATE = 'DB/mdb_allow_sample_update' # name of the config parameter storing values
    # for "allow sample updates"

    def __init__(self):  #, err_obj = None
        self.cfg = cm2.get_main_config() # ConfigData(gc.MAIN_CONFIG_FILE)  # obj_cfg
        # self.error = err_obj
        self.s_conn = self.prepare_conn_string()  # self.cfg.get_item_by_key(gc.CFG_DB_CONN).strip()
        self.conn = None

    def prepare_conn_string(self):
        # get connection string template
        conn_str = self.cfg.get_item_by_key('DB/mdb_conn_str').strip()
        # get values for connection string components
        server = os.environ.get(self.cfg.get_item_by_key('DB/env_db_server').strip())
        dbname = os.environ.get(self.cfg.get_item_by_key('DB/env_db_name').strip())
        user_name = os.environ.get(self.cfg.get_item_by_key('DB/env_db_user_name').strip())
        user_pwd = os.environ.get(self.cfg.get_item_by_key('DB/env_db_user_pwd').strip())
        # get values for connection string components' place holders
        server_plh = self.cfg.get_item_by_key('DB/db_plh_server').strip()
        dbname_plh = self.cfg.get_item_by_key('DB/db_plh_db_name').strip()
        user_name_plh = self.cfg.get_item_by_key('DB/db_plh_user_name').strip()
        user_pwd_plh = self.cfg.get_item_by_key('DB/db_plh_user_pwd').strip()
        # update connection string template with retrieved values
        conn_str = conn_str.replace(server_plh, server)
        conn_str = conn_str.replace(dbname_plh, dbname)
        conn_str = conn_str.replace(user_name_plh, user_name)
        conn_str = conn_str.replace(user_pwd_plh, user_pwd)
        return conn_str

    def open_connection(self):
        self.conn = pyodbc.connect(self.s_conn, autocommit=True)

    def run_sql_request(self,
                        logger_obj,  # logger obj to be used to pass log entries to
                        error_obj,  # error obj to be used to pass errors to
                        process_name,
                        sql_str):
        result = None
        columns = None

        if not self.conn:
            self.open_connection()
        # sql_str = self.cfg.get_item_by_key('DB/sp_rpt_lstsbycateg').strip()
        if logger_obj:
            logger_obj.info('SQL call = {}'.format(sql_str))

        try:
            cursor = self.conn.cursor()
            cursor.execute(sql_str)

            # returned recordsets
            columns = cursor.description
            if columns:
                # if some data was returned
                result = [{columns[index][0]: column for index, column in enumerate(value)} for value in cursor.fetchall()]
            else:
                # no data was returned and no errors were reported
                result = []

            return result, columns

        except Exception as ex:
            # report an error if DB call has failed.
            _str = 'Error "{}" occurred during execution of "{}"; ' \
                   'used SQL script "{}". Here is the traceback: \n{} '.format(
                    ex, process_name, sql_str, traceback.format_exc())
            error_obj.add_error(_str, send_email=True)
            if logger_obj:
                logger_obj.error(_str)

