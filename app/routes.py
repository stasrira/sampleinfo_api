from app import app
from flask import request, jsonify, send_from_directory, render_template, redirect, url_for, flash
from flask_login import login_required
from werkzeug.urls import url_parse
from datetime import datetime
import inspect
import os
from utils import common2 as cm2, global_const as gc, scheduler
from utils import reports as rp
from swagger.api_spec import spec
import pandas as pd
import json
from errors import WebError
from flask_login import current_user, login_user
from utils import User


@app.route('/')
@app.route('/index')
@app.route('/api')
def index():
    # verify main app settings and get config and logging references
    mcfg = cm2.get_main_config()
    # mlog, mlog_handler = cm2.get_logger(cm2.get_client_ip())
    env_validated = cm2.check_env_variables(__file__)

    if mcfg and env_validated:
        request_datetime = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        return jsonify(message = 'SealfonLab SampleInfo API Up and Running. Date: {}. '
                                 'For more details navigate to {}/api/docs'
                       .format(request_datetime, request.base_url), status = 200)
    else:
        err_code = 400
        return jsonify(message = 'SealfonLab SampleInfo API - Errors encountered during retrieving data.',
                       status = err_code), err_code

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

@app.before_first_request
def _run_on_start():
    # get reference for the main config file
    mcfg = cm2.get_main_config()
    # get a config value defining if the custom logging should be used
    custom_logging = mcfg.get_value('Logging/custom_logging')
    if isinstance(custom_logging, bool):
        gc.custom_logging = custom_logging
    else:
        # assign False as a default
        gc.custom_logging = False

    # start scheduler to delete old log files
    scheduler.init_scheduler()
    # run first cleaning event on the start up
    cm2.clean_log_directory()

@app.route('/test_error_handling')
def test_error_handling():
    request_datetime = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    er1 = 0
    test = 2 / er1
    return jsonify(message = 'Response from test endpoint "test_error_handling". Date: {}. '
                       .format(request_datetime), status = 200)

# returns aliqout dataset stats
@app.route('/api/sampleinfo/stats')
def api_sampleinfo_stats():
    """
    ---
    get:
      description: Retrieves statistic information for all SamlpeInfo datasets
      responses:
        '200':
          description: call successful
          content:
            application/json:
              schema: OutputSchema
      tags:
          - statistic info
    """
    response, status = generate_view ('sql_view_aliquot_data_stats')
    return response, status

# returns metadata stats dataset
@app.route('/api/metadata/stats')
def api_metadata_stats():
    """
    ---
    get:
      description: Retrieves statistic information for all Metadata datasets
      responses:
        '200':
          description: call successful
          content:
            application/json:
              schema: OutputSchema
      tags:
          - statistic info
    """
    response, status = generate_view('sql_view_metadata_stats')
    return response, status

# returns metadata dataset for the given study_id parameter (required)
# accepts the following optional parameters: study_group_id, sample_ids, sample_delim
# optional parameters can be provided as get or post parameters
@app.route('/api/metadata/study/<study_id>', methods=('get', 'post'))
def api_metadata_by_study(study_id):
    """
    ---
    get:
      description: Retrieves Metadata dataset based on the provided study_id value
      parameters:
        - name: study_id
          in: path
          description: study_id
          type: integer
          required: true
      responses:
        '200':
          description: call successful
          content:
            application/json:
              schema: OutputSchema
      tags:
          - metadata
    post:
      description: Retrieves Metadata dataset based on the provided study_id value
      parameters:
        - name: study_id
          in: path
          description: study_id
          type: integer
          required: true
      responses:
        '200':
          description: call successful
          content:
            application/json:
              schema: OutputSchema
      tags:
          - metadata
    """
    # get request parameters from get or post, from query string or form
    sample_ids = request.values.get('sample_ids')
    sample_delim = request.values.get('sample_delim')
    center_id = request.values.get('center_id')
    # body_json = request.json  # get json parameter - not in use here

    return generate_metadata_dataset (study_id, center_id, sample_ids, sample_delim)

# returns metadata dataset for the given study_group_id parameter (required)
# accepts the following optional parameters: study_id, sample_ids, sample_delim
# optional parameters can be provided as get or post parameters
@app.route('/api/metadata/center/<center_id>', methods=('get', 'post'))
def api_metadata_by_center(center_id):
    """
    ---
    get:
      description: Retrieves Metadata dataset based on the provided center_id value
      parameters:
        - name: center_id
          in: path
          description: center_id
          type: integer
          required: true
      responses:
        '200':
          description: call successful
          content:
            application/json:
              schema: OutputSchema
      tags:
          - metadata
    post:
      description: Retrieves Metadata dataset based on the provided center_id value
      parameters:
        - name: center_id
          in: path
          description: center_id
          type: integer
          required: true
      responses:
        '200':
          description: call successful
          content:
            application/json:
              schema: OutputSchema
      tags:
          - metadata
    """
    # get request parameters from get or post, from query string or form
    sample_ids = request.values.get('sample_ids')
    sample_delim = request.values.get('sample_delim')
    study_id = request.values.get('study_id')

    return generate_metadata_dataset(study_id, center_id, sample_ids, sample_delim)

# returns aliquot dataset for the given study_group_ids and dataset type id parameters (both are required)
# accepts the following optional parameters: aliquot_ids, aliquot_delim, aliquot_id_contains
# optional parameters can be provided as get or post parameters
@app.route('/api/sampleinfo/center_datasettype/<center_ids>/<dataset_type_id>', methods=('get', 'post'))
def api_sampleinfo_by_studygroup_datasettype(center_ids, dataset_type_id):
    """
    ---
    get:
      description: Retrieves SampleInfo dataset based on the provided "in-path" center_ids and dataset_type_id values with some optional "query" parameters
      parameters:
        - name: center_ids
          in: path
          description: center_ids
          type: string
          required: true
        - name: dataset_type_id
          in: path
          description: dataset_type_id
          type: integer
          required: true
        - name: aliquot_ids
          in: query
          description: aliquot_ids
          type: string
          required: false
        - name: aliquot_delim
          in: query
          description: aliquot_delim
          type: string
          required: false
        - name: aliquot_id_contains
          in: query
          description: aliquot_id_contains
          type: string
          required: false
      responses:
        '200':
          description: call successful
          content:
            application/json:
              schema: OutputSchema
      tags:
          - sampleinfo
    post:
      description: Retrieves SampleInfo dataset based on the provided "in-path" center_ids and dataset_type_id values with some optional "query" parameters
      parameters:
        - name: center_ids
          in: path
          description: center_ids
          type: string
          required: true
        - name: dataset_type_id
          in: path
          description: dataset_type_id
          type: integer
          required: true
        - name: aliquot_ids
          in: query
          description: aliquot_ids
          type: string
          required: false
        - name: aliquot_delim
          in: query
          description: aliquot_delim
          type: string
          required: false
        - name: aliquot_id_contains
          in: query
          description: aliquot_id_contains
          type: string
          required: false
      responses:
        '200':
          description: call successful
          content:
            application/json:
              schema: OutputSchema
      tags:
          - sampleinfo
    """

    # get request parameters from get or post, from query string or form
    aliquot_ids = request.values.get('aliquot_ids')
    aliquot_delim = request.values.get('aliquot_delim')
    aliquot_id_contains = request.values.get('aliquot_id_contains')
    return generate_sampleinfo_dataset(center_ids, dataset_type_id, aliquot_ids, aliquot_delim, aliquot_id_contains)
    # return 'api_sampleinfo_dataset, study_group_id = {}, sample ids = {}, sample_delim = {}, study_id = {}'. \
    #     format(study_group_id, sample_ids, sample_delim, study_id)

# returns aliquot dataset, all parameters are optional. Default value of the dataset_type_id is 1.
# accepts the following optional parameters: study_group_ids, dataset_type_id, aliquot_ids,
# aliquot_delim, aliquot_id_contains
# optional parameters can be provided as get or post parameters
@app.route('/api/sampleinfo/dataset/', methods=('get', 'post'))
def api_sampleinfo_dataset():
    """
    ---
    get:
      description: Retrieves SampleInfo dataset based on the provided "query" center_ids and dataset_type_id values with some optional "query" parameters
      parameters:
        - name: center_ids
          in: query
          description: center_ids
          type: string
          required: true
        - name: dataset_type_id
          in: query
          description: dataset_type_id
          type: integer
          required: true
        - name: aliquot_ids
          in: query
          description: aliquot_ids
          type: string
          required: false
        - name: aliquot_delim
          in: query
          description: aliquot_delim
          type: string
          required: false
        - name: aliquot_id_contains
          in: query
          description: aliquot_id_contains
          type: string
          required: false
      responses:
        '200':
          description: call successful
          content:
            application/json:
              schema: OutputSchema
      tags:
          - sampleinfo
    post:
      description: Retrieves SampleInfo dataset based on the provided "query" center_ids and dataset_type_id values with some optional "query" parameters
      parameters:
        - name: center_ids
          in: query
          description: center_ids
          type: string
          required: true
        - name: dataset_type_id
          in: query
          description: dataset_type_id
          type: integer
          required: true
        - name: aliquot_ids
          in: query
          description: aliquot_ids
          type: string
          required: false
        - name: aliquot_delim
          in: query
          description: aliquot_delim
          type: string
          required: false
        - name: aliquot_id_contains
          in: query
          description: aliquot_id_contains
          type: string
          required: false
      responses:
        '200':
          description: call successful
          content:
            application/json:
              schema: OutputSchema
      tags:
          - sampleinfo
    """
    # get request parameters from get or post, from query string or form
    aliquot_ids = get_web_request_value(request, 'aliquot_ids')  # request.values.get('aliquot_ids')
    aliquot_delim = get_web_request_value(request, 'aliquot_delim')  # request.values.get('aliquot_delim')
    aliquot_id_contains = get_web_request_value(request, 'aliquot_id_contains')  # request.values.get('aliquot_id_contains')
    dataset_type_id = get_web_request_value(request, 'dataset_type_id')  # request.values.get('dataset_type_id')
    center_ids = get_web_request_value(request, 'center_ids')  # request.values.get('center_ids')
    return generate_sampleinfo_dataset(center_ids, dataset_type_id, aliquot_ids, aliquot_delim, aliquot_id_contains)
    # return 'api_sampleinfo_dataset, study_group_id = {}, sample ids = {}, sample_delim = {}, study_id = {}'. \
    #     format(study_group_id, sample_ids, sample_delim, study_id)

@app.route("/api/swagger.json")
def create_swagger_spec():
    return jsonify(spec.to_dict())

@app.route('/login', methods=['GET', 'POST'])
def login():
    import hashlib

    if current_user.is_authenticated:
        return redirect(url_for('view_reports'))  # TODO: update url to be redirected

    next_page = get_web_request_value(request, 'next')
    if not next_page or url_parse(next_page).netloc != '':
        next_page = ''

    if request.method == 'GET':
        # proceed here if GET method was used (first time visit)
        return render_template('login.html', next_page=next_page)

    # get submitted parameters
    # user_name = get_web_request_value(request, 'user')
    user_name = cm2.get_client_ip() + os.environ.get('ST_USER_NAME_POSTFIX')
    pwd = get_web_request_value(request, 'pwd')
    pwd = hashlib.md5(str(pwd).encode('utf-8')).hexdigest()
    remember_me = True if get_web_request_value(request, 'remember_me') else False

    user = User()
    user = user.get_user(user_name)

    if user is None or not user.check_password(pwd):
        error_num = 401
        # error_details = {
        #     'error_msg': 'Invalid credentials were supplied - try again. '
        #                  'Contact admin if you need help with authentication.',
        # }
        # err_msg = render_template('display_message.html', error_details=error_details)
        flash('Invalid credentials were supplied. Contact admin if you need help with authentication.')
        # return redirect(url_for('login'))
        return render_template('login.html', next_page=next_page, remember_me=remember_me), error_num

    # save user to the session
    login_user(user, remember = remember_me)  # remember=True

    # list of call back urls used by view_reports
    view_report_ajax_calls = ['/get_report_filters', '/get_report_data']
    # adjust next_page value if it is not set or belongs to some of the ajax call backs used by view_reports
    if not next_page or next_page in view_report_ajax_calls:
        next_page = url_for('view_reports')
    return redirect(next_page)

@app.route('/view_reports', methods=['GET', 'POST'])
@login_required
def view_reports():
    mcfg = cm2.get_main_config()
    webrep_cfg = cm2.get_webreports_config()

    # get list of available reports from the config
    cfg_rep_loc = 'WebReports/SampleInfo'
    reports = webrep_cfg.get_value(cfg_rep_loc)
    # get environment name
    env_name = os.environ.get(mcfg.get_item_by_key('Email/env_name').strip())  # get environment name
    if not env_name:
        env_name = 'Not Defined'

    if reports:
        return render_template("view_report.html", reports = reports, environment = env_name)
    else:
        # mcfg = cm2.get_main_config()
        mlog, mlog_handler = cm2.get_logger()
        process_name = inspect.stack()[0][3]
        err = WebError(process_name, mcfg, mlog)

        _str = 'No list of available reports found in the config, check value of the "{}" parameter. ' \
               'An alert email was sent to the administrator.' \
            .format(cfg_rep_loc)
        error_num = 510

        mlog.info(_str)
        err.add_error(_str,error_num, True)

        cm2.stop_logger(mlog, mlog_handler)

        error_details = {
            'error_msg': _str,
            'error_num': str(error_num),
            'instructions': 'Please try to reload this webpage. If the error persists, contact the administrator.',
            'error_title': 'ERROR!'
        }
        return render_template('display_message.html', error_details=error_details, stand_by_itself = True), error_num

        # mlog, mlog_handler = cm2.get_logger()
        # mlog.info('No list of available reports found in the config, check value of the "{}" parameter.'.format(cfg_rep_loc))
        # cm2.stop_logger(mlog, mlog_handler)
        # return render_template('error.html', report_name="View Reports", error = "No list of available reports found.")

@app.route('/get_report_filters', methods=('get', 'post'))
@login_required
def get_report_filters():
    err = None
    cfg_rep_loc = 'WebReports/SampleInfo'
    webrep_cfg = cm2.get_webreports_config()

    filters_out = {}

    req_report_id = get_web_request_value(request, 'report_id')
    req_program_id = get_web_request_value(request, 'cur_program_id')

    if req_report_id:
        reports = webrep_cfg.get_value(cfg_rep_loc)
        for rep in reports:
            if rep['rep_id'] == req_report_id:
                if 'filters' in rep:
                    filters = rep['filters']
                    if filters:
                        for filter in filters:
                            data, err = get_filter_values(filter)
                            if data and 'result' in data and 'id' in data:
                                # some data was returned
                                filters_out[data['id']] = data
                            if err and err.exist():
                                # some error occurred during getting filter data
                                break
    if err is None or not err.exist():
        # no errors were reported
        cur_program_id = int(req_program_id if req_program_id and req_program_id.isnumeric() else -1)
        return render_template('report_filters.html', filters=filters_out, cur_program_id = cur_program_id)
    else:
        error_num = 511
        error_details = {
            'error_msg': 'An unexpected error was encountered during loading report filters. '
                         'An alert email was sent to the administrator.',
            'error_num': str(error_num),
            'instructions': 'Note: Previously selected filters were reset. Please make a new selection.',
            'error_title': 'ERROR!'
        }
        return render_template('display_message.html', error_details = error_details), error_num

@app.route('/get_report_data', methods=('get', 'post'))
@login_required
def get_report_data():
    cfg_rep_loc = 'WebReports/SampleInfo'
    mcfg = cm2.get_main_config()
    webrep_cfg = cm2.get_webreports_config()

    mlog, mlog_handler = cm2.get_logger()
    process_name = inspect.stack()[0][3]

    sql = ''
    report_name = ''
    report_id = ''

    # get id of the requested report
    req_report_id = get_web_request_value(request, 'report_id')

    if req_report_id:
        reports = webrep_cfg.get_value(cfg_rep_loc)  # get list of reports from the config file
        for rep in reports:
            if rep['rep_id'] == req_report_id:  # request.form['report_id']:
                parameters = {}
                report_name = rep['rep_name']  # get report name from the config
                report_id = rep['rep_id']  # get report id into a separate variable  TODO: check if this assignment can be removed
                # get sql statement
                if 'sql' in rep:
                    # get dataset name (corresponds to an entry in the main config file under DB/ section) for the SQL command to be used
                    dataset_name = rep['sql']

                # collect expected parameters and update sql statement
                if 'filters' in rep:
                    filters = rep['filters']
                    if filters:
                        for flt in filters:
                            if 'id' in flt:
                                val = get_web_request_value(request, flt['id'])
                                if not val is None:
                                    parameters[flt['id']] = val
                                # if flt['id'] in request.form:
                                #     parameters [flt['id']] = request.form[flt['id']]

                # get column report filters
                column_report_filters_str = get_web_request_value(request, 'column_report_filters')

                # check if get_csv_file_only is provided and proceed with allowing to download data
                # instead of showig the report
                get_csv_file_only_str = get_web_request_value(request, 'get_csv_file_only')
                if get_csv_file_only_str and get_csv_file_only_str == 'yes':
                    get_csv_file_only = True
                else:
                    get_csv_file_only = False

                # get the dataset from the database
                result, columns, err = rp.get_dataset(mcfg, mlog, dataset_name, **parameters)

                # check for errors and create an output
                if err and not err.exist():
                    if result:
                        df = pd.DataFrame(result)

                        # if the requested report should be displayed on a portal (vs. being provided as csv file)
                        if not get_csv_file_only:

                            # get max number of rows to show on web page from the config file
                            max_rows = mcfg.get_item_by_key('Report/max_web_rows_to_show')
                            if not max_rows.isnumeric():
                                max_rows = 1000  # use default value if nothing is provided in the config file
                            else:
                                max_rows = int(max_rows)

                            filters_applied = False
                            # check if column filters were provided from UI and apply them to the DB dataset
                            if column_report_filters_str and len(column_report_filters_str) > 0:
                                column_report_filters = json.loads(column_report_filters_str)
                                for cl_fl in column_report_filters:
                                    for item in cl_fl:
                                        if len(cl_fl[item]) > 0:
                                            # for each not empty filter, find a corresponding column and apply the filter's
                                            # value to keep only matching records
                                            # astype(str) - used to convert any provided column to a string format
                                            # regex=False - avoids checking filter's values for regex, improves speed
                                            # na=False - avoids errors if not filled rows are present
                                            # case=False - allows case insensitive search
                                            df = df[df[item].astype(str).str.contains(
                                                cl_fl[item], regex=False, na=False, case=False)]
                                            filters_applied = True

                            # check if any columns have to be deleted from the final dataset based on the config
                            if 'remove_columns_from_dataset' in rep:
                                # if the current report has assigned columns to be deleted from the data frame
                                delete_columns = rep['remove_columns_from_dataset']
                                if delete_columns:
                                    # loop through the list of columns and delete them one by one
                                    for del_col in delete_columns:
                                        if del_col in df.columns:  # check if column exists in the dataframe
                                            df = df.drop(del_col, 1)

                            # get the latest list of columns out of the current dataframe object
                            columns_to_web = [ (col,'') for col in df.columns ]

                            # if number of rows in the df over the max, take first records upto the maximum count
                            if df.shape[0] > max_rows:
                                result1 = df.iloc[0:max_rows].to_dict('records')
                            else:
                                result1 = df.to_dict('records')
                                max_rows_msg = ''

                            if len(result) > max_rows:
                                if filters_applied:
                                    # column filters were applied, prepare a message to display
                                    if df.shape[0] > max_rows:
                                        # not all filtered rows can be displayed on the website
                                        max_rows_msg = '*Note: Column filters were applied - first {} rows are ' \
                                                       'displayed out of {} filtered records received from the ' \
                                                       'database. Use more detailed filtering if required ' \
                                                       'records are not shown.' \
                                            .format(len(result1), df.shape[0])
                                    else:
                                        # all filtered rows can be displayed on the website
                                        max_rows_msg = '*Note: Column filters were applied - all {} filtered rows ' \
                                                       'received from the database are displayed.' \
                                            .format(len(result1))
                                else:
                                    max_rows_msg = '*Note: only first {} rows are displayed out of {} records returned ' \
                                                   'by the database. Use more detailed filtering if required records ' \
                                                   'are not shown. ' \
                                        .format(len(result1), len(result))

                            # some dataset was returned from the DB
                            if mlog:
                                mlog.info('Received response from DB for requested report id "{}", '
                                          'proceeding to render the web response.'.format(report_id))
                                cm2.stop_logger(mlog, mlog_handler)
                            return render_template('report_data.html', report_name=report_name, columns=columns_to_web,
                                                   data=result1, max_rows_msg = max_rows_msg,
                                                   column_report_filters = column_report_filters_str)
                        else:
                            # proceed here if the report has to be provided as a csv file for a download
                            import time
                            # prepare name for the download file
                            ts = time.strftime("%Y%m%d_%H%M%S", time.localtime())
                            temp_dld_file_name = str(ts + '_' + report_name + '.csv').replace(' ', '_')

                            # get csv content of the dataset being downloaded
                            csv = df.to_csv(None, encoding='utf-8', index=False)

                            return jsonify(csv=csv, file_name = temp_dld_file_name)

                    else:
                        # No dataset was returned from the DB
                        _str = 'No data was returned from the database for the requested parameters.'
                        error_details = {
                            'error_msg': _str,
                            # 'error_num': '',
                            # 'instructions': '',
                            'error_level': 'secondary',
                            # 'error_title': 'No Data'
                        }
                        return render_template('display_message.html', error_details=error_details)
                        # return render_template('no_report_data.html', msg=_str, text_color = 'black')
                else:
                    _str = 'An unexpected error was encountered during retrieving data for "{}" report ' \
                           '(report_id = {}). An email notification has been sent to the administrator. '\
                        .format(report_name, report_id)
                    if mlog:
                        mlog.info('Proceeding to report the following error to the web page: '.format(_str))
                        cm2.stop_logger(mlog, mlog_handler)

                    error_num = 512
                    error_details = {
                        'error_msg': _str,
                        'error_num': str(error_num),
                        'instructions': 'Please try to rerun the report, if errors persist, contact the administrator.',
                        # 'error_level': 'warning',
                        'error_title': 'ERROR!'
                    }
                    return render_template('display_message.html', error_details=error_details), error_num

                    # return render_template('error.html', report_name=report_name, error=_str)

                # get out of the loop if the report was found
                break

def get_web_request_value (request, field_name):
    # get requested value based on the method of the request
    value_out = None
    if request.method == 'GET':
        value_out = request.values.get(field_name)
    elif request.method == 'POST':
        if field_name in request.form:
            value_out = request.form[field_name]
    return value_out

def generate_view(view_name):
    mcfg = cm2.get_main_config()
    mlog, mlog_handler = cm2.get_logger(cm2.get_client_ip())
    process_name = inspect.stack()[1][3]

    if mlog:
        mlog.info('Processing request from "{}" for generating "{}" view.'.format(process_name, view_name))

    # get the dataset from the database
    result, columns, err = rp.get_veiw_data (mcfg, mlog, view_name)

    # check for errors and create an output
    if err and not err.exist():
        status = 200
        if mlog:
            mlog.info('Received response from DB, proceeding to render the api response.')
            cm2.stop_logger(mlog, mlog_handler)
        return jsonify(data=result, status=status), status
    else:
        status = 400
        mlog.info('Proceeding to report an error.')
        cm2.stop_logger(mlog, mlog_handler)
        return jsonify(message = 'Error retrieving data', status = status), status

def generate_metadata_dataset (study_id, center_id, sample_ids, sample_delim):
    mcfg = cm2.get_main_config()
    mlog, mlog_handler = cm2.get_logger(cm2.get_client_ip())
    process_name = inspect.stack()[1][3]
    dataset_name = 'sql_sp_metadata'

    if mlog:
        mlog.info('Processing request from "{}" for generating metadata dataset.'.format(process_name))

    # get the dataset from the database
    result, columns, err = rp.get_dataset(mcfg, mlog, dataset_name,
                                          study_id = study_id, center_id = center_id,
                                          sample_ids = sample_ids, sample_delim = sample_delim)

    # check for errors and create an output
    if err and not err.exist():
        if mlog:
            mlog.info('Received response from DB, proceeding to render the api response.')
            cm2.stop_logger(mlog, mlog_handler)
        return jsonify(data = result, status = 200)
    else:
        if mlog:
            mlog.info('Proceeding to report an error.')
            cm2.stop_logger(mlog, mlog_handler)
        return jsonify(message = 'Error retrieving data', status = 400)

def generate_sampleinfo_dataset (center_ids, dataset_type_id, aliquot_ids, aliquot_delim, aliquot_id_contains):
    mcfg = cm2.get_main_config()
    mlog, mlog_handler = cm2.get_logger(cm2.get_client_ip())
    process_name = inspect.stack()[1][3]
    dataset_name = 'sql_sp_sampleinfo_dataset'

    if mlog:
        mlog.info('Processing request from "{}" for generating sampleinfo dataset.'.format(process_name))

    # get the dataset from the database
    result, columns, err = rp.get_dataset(mcfg, mlog, dataset_name,
                                          center_ids = center_ids, dataset_type_id = dataset_type_id,
                                          aliquot_ids = aliquot_ids, aliquot_delim = aliquot_delim,
                                          aliquot_id_contains = aliquot_id_contains)

    # check for errors and create an output
    if err and not err.exist():
        if mlog:
            mlog.info('Received response from DB, proceeding to render the api response.')
            cm2.stop_logger(mlog, mlog_handler)
        return jsonify(data=result, status=200)
    else:
        if mlog:
            mlog.info('Proceeding to report an error.')
            cm2.stop_logger(mlog, mlog_handler)
        return jsonify(message = 'Error retrieving data', status = 400)

def get_filter_values(filter):
    mcfg = cm2.get_main_config()
    mlog, mlog_handler = cm2.get_logger()
    result = None
    columns = None
    err = None
    filter_data = {}
    filter_id_str = 'unknown'
    filter_name_str = 'unknown'
    filter_data_type = 'text'
    filter_dropdown_default_value = None
    filter_add_blank_option = None

    if filter and isinstance(filter, dict):
        if 'id' in filter:
            filter_id_str = filter['id']
        if 'name' in filter:
            filter_name_str = filter['name']
        if 'type' in filter:
            filter_data_type = filter['type']
        if 'dropdown_default_value' in filter:
            filter_dropdown_default_value = filter['dropdown_default_value']
        if 'add_blank_option' in filter:
            filter_add_blank_option = filter['add_blank_option']
        if 'id' in filter and filter['id'] in ['program_id', 'center_id', 'center_ids', 'study_id', 'dataset_type_id']:
            result, columns, err = rp.get_filter_data(mcfg, mlog, filter['id'])

        # if result is not populated yet and options are present in the config
        if not result and 'options' in filter:
            result = []
            for opt in filter['options']:
                result.append({'option_id': opt['id'], 'option_name': opt['name']})

        if not err or not err.exist():
            # no errors reported
            filter_data['id'] = filter_id_str
            filter_data['name'] = filter_name_str
            filter_data['result'] = result
            filter_data['type'] = filter_data_type
            if filter_dropdown_default_value:
                filter_data['dropdown_default_value'] = filter_dropdown_default_value
            if filter_add_blank_option:
                filter_data['add_blank_option'] = filter_add_blank_option
            # filter_data['columns'] = columns
        elif err.exist():
            filter_data = None

    return filter_data, err
