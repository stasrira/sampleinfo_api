from sampleinfo import app
from os import environ, path
from dotenv import load_dotenv

if __name__ == "__main__":
    # load environment variables from files
    basedir = path.abspath(path.dirname(__file__))
    load_dotenv(path.join(basedir, '.flaskenv'))
    load_dotenv(path.join(basedir, '.env'))

    app.run()