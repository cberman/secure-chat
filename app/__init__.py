from flask import Flask
from werkzeug import utils

app = Flask(__name__)

try:
    app.config.from_object('config')
except utils.ImportStringError:
    from os import path, urandom
    basedir = path.abspath(path.dirname(__file__))
    app.config.update(
            DATABASE=path.join(basedir, 'chat.db'),
            DEBUG=False,
            SECRET_KEY=urandom(24),
    )

import views, database
