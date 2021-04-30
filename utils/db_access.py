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
        logger_obj.info('SQL call = {}'.format(sql_str))

        try:
            cursor = self.conn.cursor()
            cursor.execute(sql_str)
            # returned recordsets

            columns = cursor.description
            result = [{columns[index][0]: column for index, column in enumerate(value)} for value in cursor.fetchall()]

            return result, columns

        except Exception as ex:
            # report an error if DB call has failed.
            _str = 'Error "{}" occurred during execution of "{}"; ' \
                   'used SQL script "{}". Here is the traceback: \n{} '.format(
                    ex, process_name, sql_str, traceback.format_exc())
            error_obj.add_error(_str)
            logger_obj.error(_str)

    # report: latest status by action group
    def run_rpt_tr_lstsbyactgrp(self,
                                logger_obj,  # logger obj to be used to pass log entries to
                                error_obj,  # error obj to be used to pass errors to
                                process_name):

        str_proc = self.cfg.get_item_by_key('DB/sp_rpt_lstsbyactgrp').strip()

        result, columns = self.run_sql_request (logger_obj, error_obj, process_name, str_proc)
        return result, columns

    # # filters: list of programs
    # def run_get_programs(self,
    #                             logger_obj,  # logger obj to be used to pass log entries to
    #                             error_obj,  # error obj to be used to pass errors to
    #                             process_name):
    #     str_proc = self.cfg.get_item_by_key('DB/sql_get_programs').strip()
    #
    #     result, columns = self.run_sql_request(logger_obj, error_obj, process_name, str_proc)
    #     return result, columns
    #
    # # filters: list of programs
    # def run_get_studies(self,
    #                      logger_obj,  # logger obj to be used to pass log entries to
    #                      error_obj,  # error obj to be used to pass errors to
    #                      process_name):
    #     str_proc = self.cfg.get_item_by_key('DB/sql_get_studies').strip()
    #
    #     result, columns = self.run_sql_request(logger_obj, error_obj, process_name, str_proc)
    #     return result, columns


    #report: latests status by category
    def run_rpt_tr_lstsbycateg(self,
                               logger_obj,  # logger obj to be used to pass log entries to
                               error_obj,  # error obj to be used to pass errors to
                               process_name):

        str_proc = self.cfg.get_item_by_key('DB/sp_rpt_lstsbycateg').strip()

        result, columns = self.run_sql_request(logger_obj, error_obj, process_name, str_proc)
        return result, columns

        # if not self.conn:
        #     self.open_connection()
        # str_proc = self.cfg.get_item_by_key('DB/sp_rpt_lstsbycateg').strip()
        # logger_obj.info('SQL Procedure call = {}'.format(str_proc))
        #
        # try:
        #     cursor = self.conn.cursor()
        #     cursor.execute(str_proc)
        #     # returned recordsets
        #
        #     columns = cursor.description
        #     result = [{columns[index][0]: column for index, column in enumerate(value)} for value in cursor.fetchall()]
        #
        #     return result, columns
        #
        # except Exception as ex:
        #     # report an error if DB call has failed.
        #     _str = 'Error "{}" occurred during execution of "{}"; ' \
        #            'used SQL script "{}". Here is the traceback: \n{} '.format(
        #             ex, process_name, str_proc, traceback.format_exc())
        #     error_obj.add_error(_str)
        #     logger_obj.error(_str)

    def submit_row(self,
                   sample_id,  # sample id of the records being submitted
                   row_json,  # row of data being submitted in JSON format
                   dict_json,  # structure of the row being submitted (dictionary) in JSON format
                   data_source_name,  # name of the source of data to be passed to DB (file path, etc.)
                   logger_obj,  # logger obj to be used to pass log entries to
                   error_obj  # error obj to be used to pass errors to
                   ):

        # dict_json = file.get_file_dictionary_json(True)
        # filepath = str(file.filepath)
        # sample_id = row.sample_id
        # row_json = row.to_json()

        if not self.conn:
            self.open_connection()
        str_proc = self.cfg.get_item_by_key(gc.CFG_DB_SQL_PROC).strip()
        study_id = self.study_cfg.get_item_by_key(gc.CFG_DB_STUDY_ID).strip()
        dict_path = '$.' + self.study_cfg.get_item_by_key(gc.CFG_DICT_PATH).strip()
        dict_upd = self.study_cfg.get_item_by_key(gc.CFG_DB_ALLOW_DICT_UPDATE).strip()
        sample_upd = self.study_cfg.get_item_by_key(gc.CFG_DB_ALLOW_SAMPLE_UPDATE).strip()

        # prepare stored proc string to be executed
        str_proc = str_proc.replace(self.cfg.get_item_by_key(gc.CFG_FLD_TMPL_STUDY_ID), study_id)  # '{study_id}'
        str_proc = str_proc.replace(self.cfg.get_item_by_key(gc.CFG_FLD_TMPL_SAMPLE_ID), sample_id)  # '{sample_id}'
        str_proc = str_proc.replace(self.cfg.get_item_by_key(gc.CFG_FLD_TMPL_ROW_JSON), row_json)  # '{smpl_json}'
        str_proc = str_proc.replace(self.cfg.get_item_by_key(gc.CFG_FLD_TMPL_DICT_JSON), dict_json)  # '{dict_json}'
        str_proc = str_proc.replace(self.cfg.get_item_by_key(gc.CFG_FLD_TMPL_DICT_PATH), dict_path)  # '{dict_path}'
        str_proc = str_proc.replace(self.cfg.get_item_by_key(gc.CFG_FLD_TMPL_FILEPATH), str(data_source_name))  # '{filepath}'
        str_proc = str_proc.replace(self.cfg.get_item_by_key(gc.CFG_FLD_TMPL_DICT_UPD), dict_upd)  # '{dict_update}'
        str_proc = str_proc.replace(self.cfg.get_item_by_key(gc.CFG_FLD_TMPL_SAMPLE_UPD), sample_upd)
        # '{samlpe_update}'

        # file.logger.info('SQL Procedure call = {}'.format(sql_str))
        logger_obj.info('SQL Procedure call = {}'.format(str_proc))
        # print ('procedure (sql_str) = {}'.format(sql_str))

        try:
            cursor = self.conn.cursor()
            cursor.execute(str_proc)
            # returned recordsets
            rs_out = []
            rows = cursor.fetchall()
            columns = [column[0] for column in cursor.description]
            results = []
            for row in rows:
                results.append(dict(zip(columns, row)))
            rs_out.append(results)
            return rs_out

        except Exception as ex:
            # report an error if DB call has failed.
            _str = 'Error "{}" occurred during submitting a row (sample_id = "{}") to database; ' \
                   'used SQL script "{}". Here is the traceback: \n{} '.format(
                    ex, sample_id, str_proc, traceback.format_exc())
            error_obj.add_error(_str)
            logger_obj.error(_str)
