from os import path, urandom
basedir = path.abspath(path.dirname(__file__))

DATABASE=path.join(basedir, 'app/chat.db')
DEBUG=False
SECRET_KEY=urandom(24)
