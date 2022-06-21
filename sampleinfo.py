from app import app
from os import environ, path


if __name__ == "__main__":

    # get host and port for running flask
    host = environ.get('FLASK_RUN_HOST')
    port = environ.get('FLASK_RUN_PORT')

    # run the Flask app
    app.run(host=host, port=port, load_dotenv=True)  #host=host, port=port, load_dotenv=True
