from app import app
from flask import request, jsonify, send_from_directory
from datetime import datetime
import inspect
import os
from utils import common2 as cm2
from utils import reports as rp
from swagger.api_spec import spec


@app.route('/')
@app.route('/index')
@app.route('/api')
def index():
    #verify main app settings and get config and logging references
    mcfg = cm2.get_main_config()
    mlog, mlog_handler = cm2.get_logger(cm2.get_client_ip())
    env_validated = cm2.check_env_variables(__file__, mlog)

    if mcfg and env_validated:
        request_datetime = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        if mlog:
            mlog.info('Successful processing of a request, reporting status 200.')
            cm2.stop_logger(mlog, mlog_handler)
        r=request
        return jsonify(message = 'SealfonLab SampleInfo API Up and Running. Date: {}. '
                                 'For more details navigate to {}/api/docs'
                       .format(request_datetime, request.base_url), status = 200)
    else:
        if mlog:
            mlog.info('Errors were reported during validating of environment variables or reading the main config file.')
            cm2.stop_logger(mlog, mlog_handler)
        return jsonify(message = 'SealfonLab SampleInfo API - Errors encountered during retrieving data.', status = 400)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

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
    return generate_view ('sql_view_aliquot_data_stats')

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
    return generate_view ('sql_view_metadata_stats')

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
    aliquot_ids = request.values.get('aliquot_ids')
    aliquot_delim = request.values.get('aliquot_delim')
    aliquot_id_contains = request.values.get('aliquot_id_contains')
    dataset_type_id = request.values.get('dataset_type_id')
    center_ids = request.values.get('center_ids')
    return generate_sampleinfo_dataset(center_ids, dataset_type_id, aliquot_ids, aliquot_delim, aliquot_id_contains)
    # return 'api_sampleinfo_dataset, study_group_id = {}, sample ids = {}, sample_delim = {}, study_id = {}'. \
    #     format(study_group_id, sample_ids, sample_delim, study_id)

@app.route("/api/swagger.json")
def create_swagger_spec():
    return jsonify(spec.to_dict())

def generate_view(view_name):
    mcfg = cm2.get_main_config()
    mlog, mlog_handler = cm2.get_logger(cm2.get_client_ip())
    # result = None
    # columns = None
    # err = None
    process_name = inspect.stack()[1][3]

    if mlog:
        mlog.info('Processing request from "{}" for generating "{}" view.'.format(process_name, view_name))

    # get the dataset from the database
    result, columns, err = rp.get_veiw_data (mcfg, mlog, view_name)

    # check for errors and create an output
    if err and not err.exist():
        if mlog:
            mlog.info('Proceeding to render the api response.')
            cm2.stop_logger(mlog, mlog_handler)
        # return jsonify(result), 200
        return jsonify(data=result, status=200)
        # return json.dumps(result, sort_keys=False)
        #     {
        #     'status': 'OK',
        #     'data': json.dumps(result, default=str)  # result
        # }
    else:
        mlog.info('Proceeding to report an error.')
        cm2.stop_logger(mlog, mlog_handler)
        return jsonify(message = 'Error retrieving data', status = 400)
        # return {
        #     'status': 'ERROR',
        #     'status_desc': 'Internal error',
        #     'data': '' # json.dumps(result, default=str)
        # }

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
            mlog.info('Proceeding to render the api response.')
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
        mlog.info('Processing request from "{}" for generating metadata dataset.'.format(process_name))

    # get the dataset from the database
    result, columns, err = rp.get_dataset(mcfg, mlog, dataset_name,
                                          center_ids = center_ids, dataset_type_id = dataset_type_id,
                                          aliquot_ids = aliquot_ids, aliquot_delim = aliquot_delim,
                                          aliquot_id_contains = aliquot_id_contains)

    # check for errors and create an output
    if err and not err.exist():
        if mlog:
            mlog.info('Proceeding to render the api response.')
            cm2.stop_logger(mlog, mlog_handler)
        return jsonify(data=result, status=200)
    else:
        if mlog:
            mlog.info('Proceeding to report an error.')
            cm2.stop_logger(mlog, mlog_handler)
        return jsonify(message = 'Error retrieving data', status = 400)
