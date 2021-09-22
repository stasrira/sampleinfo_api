from flask import Flask, jsonify
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False  # this will preserve order of the fields outputted to JSON

from app import routes

# global error handler setup
from werkzeug.exceptions import HTTPException, default_exceptions
from utils import common2 as cm2
from errors import WebError
import traceback
from flask import request
from swagger.api_spec import spec

def handle_error(error):
    code = 500
    msg = 'Internal error has occurred'

    if isinstance(error, HTTPException):
        code = error.code
    # url of the request initiated this error
    url = request.url
    # define config and log objects
    mcfg = cm2.get_main_config()
    mlog, mlog_handler = cm2.get_logger(cm2.get_client_ip())

    if code == 500:
        # if 500 error has occurred, record error in log and send email
        err = WebError('UNHANDLED ERROR', mcfg, mlog)
        _str = 'UNEXPECTED UNHANDLED ERROR "{}" occurred during processing the following URL request: "{}"; ' \
               'The original exception that has triggered the error is "{}". ' \
               'Here is the traceback: \n{} '.format(
                error.name, url, error.original_exception, traceback.format_exc())
        err.add_error(_str, code, send_email=True)
        if mlog:
            mlog.error(_str)
    else:
        # just record error in log
        msg = error.description
        if mlog:
            mlog.warning('Non-critical error has occurred during processing the following URL request: "{}". '
                         'Code: {}. Error: {}'.format(url, code, error.name))

    return jsonify(message = msg, status = code)

for exc in default_exceptions:
    app.register_error_handler(exc, handle_error)

# swagger related
with app.test_request_context():
    # register all swagger documented functions here
    for fn_name in app.view_functions:
        if fn_name == 'static':
            continue
        # print(f"Loading swagger docs for function: {fn_name}")
        view_fn = app.view_functions[fn_name]
        spec.path(view=view_fn)

from swagger import swagger_ui_blueprint, SWAGGER_URL
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)