import traceback, inspect
from errors import WebError
from utils import common2 as cm2, MetadataDB

def report_tr_lstsbycateg(mcfg, mlog, parameters = None):
    result = None
    columns = None
    report_name = 'Latest Status Grouped By Categories'
    process_name = inspect.stack()[1][3]

    err = WebError(process_name)

    # verify main app settings and get config and logging references
    env_validated = cm2.check_env_variables(__file__, mlog)
    if not env_validated:
        err.add_error('Some required environment variable were not set!')

    if mcfg and env_validated:
        try:
            mdb = MetadataDB()
            result, columns = mdb.run_rpt_tr_lstsbycateg(mlog, err, process_name)

        except Exception as ex:
            # print (ex)
            _str = 'Unexpected Error "{}" occurred during running of "{}"; ' \
                   'Here is the traceback: \n{} '.format(
                ex, process_name, traceback.format_exc())
            err.add_error(_str)
            mlog.error(_str)

    return result, columns, report_name, err

def report_tr_lstsbyactgrp(mcfg, mlog):
    result = None
    columns = None
    report_name = 'Latest Status By Action Groups'
    process_name = inspect.stack()[1][3]

    err = WebError(process_name)

    # verify main app settings and get config and logging references
    env_validated = cm2.check_env_variables(__file__, mlog)
    if not env_validated:
        err.add_error('Some required environment variable were not set!')

    if mcfg and env_validated:
        try:
            mdb = MetadataDB()
            result, columns = mdb.run_rpt_tr_lstsbyactgrp(mlog, err, process_name)

        except Exception as ex:
            # print (ex)
            _str = 'Unexpected Error "{}" occurred during running of "{}"; ' \
                   'Here is the traceback: \n{} '.format(
                ex, process_name, traceback.format_exc())
            err.add_error(_str)
            mlog.error(_str)

    return result, columns, report_name, err

def get_filter_data (mcfg, mlog, filter_id):
    result = None
    columns = None
    process_name = inspect.stack()[1][3]

    err = WebError(process_name)
    # verify main app settings and get config and logging references
    env_validated = cm2.check_env_variables(__file__, mlog)
    if not env_validated:
        err.add_error('Some required environment variable were not set!')

    if mcfg and env_validated:
        try:
            mdb = MetadataDB()
            if filter_id == 'program_id':
                #result, columns = mdb.run_get_programs(mlog, err, process_name)
                sql = mcfg.get_item_by_key('DB/sql_get_programs').strip()
                result, columns = mdb.run_sql_request(mlog, err, process_name, sql)
            if filter_id == 'study_id':
                # result, columns = mdb.run_get_studies(mlog, err, process_name)
                sql = mcfg.get_item_by_key('DB/sql_get_studies').strip()
                result, columns = mdb.run_sql_request(mlog, err, process_name, sql)

        except Exception as ex:
            # print (ex)
            _str = 'Unexpected Error "{}" occurred during running of "{}"; ' \
                   'Here is the traceback: \n{} '.format(
                ex, process_name, traceback.format_exc())
            err.add_error(_str)
            mlog.error(_str)

    return result, columns, err

def sql_view_aliquot_data_stats (mcfg, mlog):
    return get_veiw_data (mcfg, mlog, 'sql_view_metadata_stats')

def view_metadata_stats(mcfg, mlog):
    return get_veiw_data(mcfg, mlog, 'sql_view_aliquot_data_stats')

# common function to retrieve view information from DB
def get_veiw_data (mcfg, mlog, view_name):
    result = None
    columns = None
    process_name = inspect.stack()[1][3]

    err = WebError(process_name)
    # verify main app settings and get config and logging references
    env_validated = cm2.check_env_variables(__file__, mlog)
    if not env_validated:
        err.add_error('Some required environment variable were not set!')

    if mcfg and env_validated:
        try:
            sql = mcfg.get_item_by_key('DB/' + view_name).strip()
            if sql:
                mdb = MetadataDB()
                result, columns = mdb.run_sql_request(mlog, err, process_name, sql)
            else:
                _str = 'No SQL statement was retrieved from the config file the for "{}" view name'.format(view_name)
                err.add_error(_str)
                mlog.error(_str)

        except Exception as ex:
            # print (ex)
            _str = 'Unexpected Error "{}" occurred during running of "{}"; ' \
                   'Here is the traceback: \n{} '.format(
                ex, process_name, traceback.format_exc())
            err.add_error(_str)
            mlog.error(_str)

    return result, columns, err

# def get_program_ids (mcfg, mlog):
#     result = None
#     columns = None
#     process_name = inspect.stack()[1][3]
#
#     err = WebError(process_name)
#     # verify main app settings and get config and logging references
#     env_validated = cm2.check_env_variables(__file__, mlog)
#     if not env_validated:
#         err.add_error('Some required environment variable were not set!')
#
#     if mcfg and env_validated:
#         try:
#             mdb = MetadataDB()
#             result, columns = mdb.run_get_programs (mlog, err, process_name)
#
#         except Exception as ex:
#             # print (ex)
#             _str = 'Unexpected Error "{}" occurred during running of "{}"; ' \
#                    'Here is the traceback: \n{} '.format(
#                 ex, process_name, traceback.format_exc())
#             err.add_error(_str)
#             mlog.error(_str)
#
#     return result, columns, err