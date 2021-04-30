from app import app
from flask import render_template, request
from datetime import datetime
import inspect
from utils import common2 as cm2
from utils import MetadataDB
from utils import reports as rp
from errors import WebError
import json
import traceback


@app.route('/')
@app.route('/index')
def index():
    #verify main app settings and get config and logging references
    mcfg = cm2.get_main_config()
    mlog, mlog_handler = cm2.get_logger()
    env_validated = cm2.check_env_variables(__file__, mlog)

    if mcfg and env_validated:
        # test code
        test = mcfg.get_value('DB/mdb_sql_proc_load_sample')
        request_datetime = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        mlog.info('Processing web request at {}'.format(request_datetime))
        cm2.stop_logger(mlog, mlog_handler)
        return "Current date: {}<br>{}<br><br>Environment variables status: {}".format(request_datetime, test,
                                                                                    str(env_validated))
    else:
        return "Main application settings (environment variables) are not properly set, cannot continue."

@app.route('/api/sampleinfo/stats')
def api_sampleinfo_stats():
    return generate_view ('sql_view_aliquot_data_stats')

@app.route('/api/metadata/stats')
def api_metadata_stats():
    return generate_view ('view_metadata_stats')

@app.route('/api/metadata/study/<study_id>', methods=('get', 'post'))
def api_metadata_by_study(study_id):
    # get request parameters from get or post, from query string or form
    sample_ids = request.values.get('sample_ids')
    sample_delim = request.values.get('sample_delim')
    study_group_id = request.values.get('study_group_id')
    # body_json = request.json  # get json parameter - not in use here
    return 'api_metadata_dataset, center id = {}, sample ids = {}, sample_delim = {}, study_group_id = {}'.\
        format(study_id, sample_ids, sample_delim, study_group_id)

@app.route('/api/metadata/studygroup/<study_group_id>', methods=('get', 'post'))
def api_metadata_by_studygroup(study_group_id):
    # get request parameters from get or post, from query string or form
    sample_ids = request.values.get('sample_ids')
    sample_delim = request.values.get('sample_delim')
    study_id = request.values.get('study_id')
    return 'api_metadata_dataset, study_group_id = {}, sample ids = {}, sample_delim = {}, study_id = {}'.\
        format(study_group_id, sample_ids, sample_delim, study_id)

def generate_view(view_name):
    mcfg = cm2.get_main_config()
    mlog, mlog_handler = cm2.get_logger()
    result = None
    columns = None
    err = None
    process_name = inspect.stack()[1][3]

    mlog.info('Processing request from "{}" for generating "{}" view.'.format(process_name, view_name))

    if view_name == 'view_metadata_stats':
        result, columns, err = rp.view_metadata_stats(mcfg, mlog)
    if view_name == 'sql_view_aliquot_data_stats':
        result, columns, err = rp.sql_view_aliquot_data_stats(mcfg, mlog)

    if err and not err.exist():
        mlog.info('Proceeding to render the api response.')
        cm2.stop_logger(mlog, mlog_handler)
        return {
            'status': 'OK',
            'data': json.dumps(result, default=str)  # result
        }
    else:
        mlog.info('Proceeding to report an error.')
        cm2.stop_logger(mlog, mlog_handler)
        return {
            'status': 'ERROR',
            'status_desc': 'Internal error',
            'data': '' # json.dumps(result, default=str)
        }

# language = request.args.get('language')










# TODO: old code to be deleted

@app.route('/view_reports')
def view_reports():
    mcfg = cm2.get_main_config()
    cfg_rep_loc = 'Reports/Tracking'
    reports = mcfg.get_value(cfg_rep_loc)
    if reports:
        return render_template("view_report.html", reports = reports)
    else:
        mlog, mlog_handler = cm2.get_logger()
        mlog.info('No list of available reports found in the config, check value of the "{}" parameter.'.format(cfg_rep_loc))
        cm2.stop_logger(mlog, mlog_handler)
        return render_template('error.html', report_name="View Reports", error = "No list of available reports found.")

@app.route('/get_report_filters', methods=['POST'])
def get_report_filters():
    cfg_rep_loc = 'Reports/Tracking'
    mcfg = cm2.get_main_config()
    # str = ''
    filters_out = {}
    if request.method == 'POST':
        # print(request.form['report_id']) #request.form['program_id'])
        reports = mcfg.get_value(cfg_rep_loc)
        for rep in reports:
            if rep['rep_id'] == request.form['report_id']:
                if 'filters' in rep:
                    filters = rep['filters']
                    for filter in filters:
                        data = get_filter_values(filter)
                        if 'result' in data and 'id' in data:
                            filters_out[data['id']] = data
                            # if data['result']:
                            #      filters_out[data['id']] = data
                            # else:
                            #     filters_out[data['id']] = None
    cur_program_id = int((request.form['cur_program_id']) if request.form['cur_program_id'].isnumeric() else -1)
    return render_template('report_filters.html', filters=filters_out, cur_program_id = cur_program_id)

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

    # if isinstance(filter, str):
    #     filter_id_str = filter

    if filter and isinstance(filter, dict):
        if 'id' in filter:
            filter_id_str = filter['id']
        if 'name' in filter:
            filter_name_str = filter['name']
        if 'type' in filter:
            filter_data_type = filter['type']
        if 'id' in filter and filter['id'] == 'program_id':
            result, columns, err = rp.get_filter_data(mcfg, mlog, filter['id'])
        if 'id' in filter and filter['id'] == 'study_id':
            result, columns, err = rp.get_filter_data(mcfg, mlog, filter['id'])
        # if filter and isinstance(filter, dict):
        # if 'name' in filter:
        #     filter_id_str = filter['name']

        # if result is not populated yet and options are present in the config
        if not result and 'options' in filter:
            result = []
            for opt in filter['options']:
                result.append({'option_id': opt['id'], 'option_name': opt['name']})
        #if result:
        if not err or not err.exist():
            filter_data['id'] = filter_id_str
            filter_data['name'] = filter_name_str
            filter_data['result'] = result
            filter_data['type'] = filter_data_type
            # filter_data['columns'] = columns

    return filter_data

@app.route('/get_report_data', methods=['POST'])
def get_report_data():
    cfg_rep_loc = 'Reports/Tracking'
    mcfg = cm2.get_main_config()
    mlog, mlog_handler = cm2.get_logger()
    process_name = inspect.stack()[0][3]
    err = WebError(process_name)
    sql = ''
    report_name = ''
    report_id = ''
    report_request = {}
    parameters = {}

    if request.method == 'POST':
        # print(request.form['report_id']) #request.form['program_id'])
        reports = mcfg.get_value(cfg_rep_loc)
        for rep in reports:
            if rep['rep_id'] == request.form['report_id']:
                report_name = rep['rep_name']
                report_id = rep['rep_id']
                # get sql statement
                if 'sql' in rep:
                    sql = rep['sql']

                # collect expected parameters and update sql statement
                if 'filters' in rep:
                    for flt in rep['filters']:
                        if 'id' in flt:
                            if flt['id'] in request.form:
                                param_val = request.form[flt['id']]
                            else:
                                param_val = ''
                            sql = sql.replace('{' + flt['id'] + '}', param_val)
                break

        # run report against DB
        mdb = MetadataDB()
        result, columns = mdb.run_sql_request(mlog, err, process_name, sql)

        if not err.exist():
            mlog.info('Retruning data for requested report id "{}".'.format(report_id))
            cm2.stop_logger(mlog, mlog_handler)
            return render_template('report_data.html', report_name=report_name, columns=columns, data=result)
        else:
            str = 'Some errors were generated during retrieving data for "{}" report.'.format(report_name)
            mlog.info('Proceeding to report the following error to the web page: '.format(str))
            cm2.stop_logger(mlog, mlog_handler)
            return render_template('error.html', report_name=report_name, error = str)

@app.route('/test/loader')
def test_loader():
    return render_template('test_loader.html')


@app.route('/reports/lstsbycateg')
def web_report_lstsbycateg():
    mcfg = cm2.get_main_config()
    mlog, mlog_handler = cm2.get_logger()
    result, columns, report_name, err = rp.report_tr_lstsbycateg(mcfg, mlog)

    if not err.exist():
        mlog.info('Proceeding to render the web page.')
        cm2.stop_logger(mlog, mlog_handler)
        return render_template('report_standalone.html', report_name=report_name, columns=columns, data=result)
    else:
        mlog.info('Proceeding to report an error to the web page.')
        cm2.stop_logger(mlog, mlog_handler)
        return render_template('error.html', report_name=report_name)

@app.route('/api/reports/lstsbycateg')
def api_report_lstsbycateg():
    mcfg = cm2.get_main_config()
    mlog, mlog_handler = cm2.get_logger()
    result, columns, report_name, err = rp.report_tr_lstsbycateg(mcfg, mlog)

    if not err.exist():
        mlog.info('Proceeding to render the api response.')
        cm2.stop_logger(mlog, mlog_handler)
        return render_template('report_json_only.html', report_name='latest Status Grouped By Categories',
                               data ={'json': json.dumps(result, default=str)})
    else:
        mlog.info('Proceeding to report an error to the web page.')
        cm2.stop_logger(mlog, mlog_handler)
        return render_template('error.html', report_name=report_name)

@app.route('/reports/lstsbyactgrp')
def web_report_tr_lstsbyactgrp():
    mcfg = cm2.get_main_config()
    mlog, mlog_handler = cm2.get_logger()
    result, columns, report_name, err = rp.report_tr_lstsbyactgrp(mcfg, mlog)

    if not err.exist():
        mlog.info('Proceeding to render the web page.')
        cm2.stop_logger(mlog, mlog_handler)
        return render_template('report_standalone.html', report_name=report_name, columns=columns, data=result)
    else:
        mlog.info('Proceeding to report an error to the web page.')
        cm2.stop_logger(mlog, mlog_handler)
        return render_template('error.html', report_name=report_name)

@app.route('/api/reports/lstsbyactgrp')
def api_report_tr_lstsbyactgrp():
    mcfg = cm2.get_main_config()
    mlog, mlog_handler = cm2.get_logger()
    result, columns, report_name, err = rp.report_tr_lstsbyactgrp(mcfg, mlog)

    if not err.exist():
        mlog.info('Proceeding to render the api response.')
        cm2.stop_logger(mlog, mlog_handler)
        return render_template('report_json_only.html', report_name='latest Status Grouped By Categories',
                               data ={'json': json.dumps(result, default=str)})
    else:
        mlog.info('Proceeding to report an error to the web page.')
        cm2.stop_logger(mlog, mlog_handler)
        return render_template('error.html', report_name=report_name)
