from flask import Flask
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False  # this will preserve order of the fields outputted to JSON

from app import routes