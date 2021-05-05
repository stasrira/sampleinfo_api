from app import app
from os import environ, path
from dotenv import load_dotenv

if __name__ == "__main__":
    # load_dotenv('.flaskenv')

    # load environment variables from files
    basedir = path.abspath(path.dirname(__file__))
    load_dotenv(path.join(basedir, '.flaskenv'))
    load_dotenv(path.join(basedir, '.env'))

    # get host and port for running flask
    host = environ.get('FLASK_RUN_HOST')
    port = environ.get('FLASK_RUN_PORT')
    # test = environ.get('ST_DB_USER_NAME')
    app.run(host=host, port=port, load_dotenv=True)  #host=host, port=port, load_dotenv=True
