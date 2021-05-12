import traceback, inspect
from errors import WebError
from utils import common2 as cm2, MetadataDB

# common function to retrieve view information from DB
def get_veiw_data (mcfg, mlog, view_name):
    result = None
    columns = None
    process_name = inspect.stack()[1][3]

    err = WebError(process_name, mcfg, mlog)
    # verify environment variables
    env_validated, env_msg = cm2.check_env_variables(__file__, mlog)
    if not env_validated:
        err.add_error(env_msg, send_email=True)

    if mcfg and env_validated:
        try:
            sql = mcfg.get_item_by_key('DB/' + view_name).strip()
            if sql:
                mdb = MetadataDB()
                result, columns = mdb.run_sql_request(mlog, err, process_name, sql)
            else:
                _str = 'No SQL statement was retrieved from the config file the for "{}" view name'.format(view_name)
                err.add_error(_str, send_email=True)
                mlog.error(_str)

        except Exception as ex:
            # print (ex)
            _str = 'Unexpected Error "{}" occurred during running of "{}"; ' \
                   'Here is the traceback: \n{} '.format(
                ex, process_name, traceback.format_exc())
            err.add_error(_str, send_email=True)
            mlog.error(_str)

    return result, columns, err

# def tests_kwargs (**data):
#     for key, value in data.items():
#         print('key = {}, value = {}'.format(key, value))

# function retrieves dataset for the specified dataset name utilizing variable set of parameters passed through **parameters
def get_dataset (mcfg, mlog, dataset_name, **param_values):

    result = None
    columns = None
    process_name = inspect.stack()[1][3]

    err = WebError(process_name, mcfg, mlog)
    # verify environment variables
    env_validated, env_msg = cm2.check_env_variables(__file__, mlog)
    if not env_validated:
        err.add_error(env_msg, send_email=True)

    if mcfg and env_validated:
        try:
            # get stored procedure to be used for the sql call
            sql = mcfg.get_item_by_key('DB/' + dataset_name).strip()
            # get passed parameters and append them to the stored procedure
            parameters = ''
            for key, value in param_values.items():
                if value:
                    param = mcfg.get_item_by_key('DB/param_' + key).strip()
                    if param:
                        parameters = parameters + ',' if len(parameters.strip()) > 0 else ' '
                        # add a parameter to the parameters string
                        parameters = parameters + param.replace('{'+key+'}', value)
            # combine final sql string to be executed
            sql = sql + parameters

            if sql:
                mdb = MetadataDB()
                result, columns = mdb.run_sql_request(mlog, err, process_name, sql)
            else:
                _str = 'No SQL statement was retrieved from the config file the for "{}" view name'.format(dataset_name)
                err.add_error(_str, send_email=True)
                mlog.error(_str)

        except Exception as ex:
            # print (ex)
            _str = 'Unexpected Error "{}" occurred during running of "{}"; ' \
                   'Here is the traceback: \n{} '.format(
                ex, process_name, traceback.format_exc())
            err.add_error(_str, send_email=True)
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