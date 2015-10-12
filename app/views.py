from app import app
from database import get_db
from flask import g, request, redirect, render_template, session, url_for
from calendar import timegm
from time import gmtime
from os import urandom

@app.route('/')
def index():
    body = '<a href=/new>Create a new session</a>'
    return render_template('layout.html', message=body)

@app.route('/favicon.ico')
def favicon():
    return str()

@app.route('/new')
def init():
    session['identifier'] = urandom(8).encode('hex')
    session['name'] = 0
    db = get_db()
    try:
        db.execute('insert into chats values (?, ?)', [int(session['identifier'], 16), 0])
        db.commit()
    except Exception:
        return init()
    return redirect(url_for('chat', identifier=session['identifier'], _external=True))

@app.route('/<identifier>')
def chat(identifier):
    bad_session = 'identifier' not in session or session['identifier'] != identifier
    db = get_db()
    entry = db.execute('select chat from chats where chat = ?', [int(identifier,16)]).fetchone()
    if ((not entry) | bad_session):
        return redirect(url_for('index', _external=True))
    return render_template('chat.html')

@app.route('/<identifier>/join')
def join(identifier):
    db = get_db()
    entry = db.execute('select full from chats where chat = ?', [int(identifier, 16)]).fetchone()
    if (not entry) | entry[0]:
        return redirect(url_for('index', _external=True))
    session['identifier'] = identifier
    session['name'] = 1
    db.execute('update chats set full = 1 where chat = ?', [int(identifier, 16)])
    db.commit()
    return redirect(url_for('chat', identifier=identifier, _external=True))

@app.route('/<identifier>/send', methods=['POST'])
def send(identifier):
    if 'identifier' in session and session['identifier'] == identifier:
        sender = session['name']
        db = get_db()
        db.execute('insert into messages values (?, ?, ?, ?, ?)',
                [int(identifier, 16), session['name'], session['name'] ^ 1, request.form['message'], timegm(gmtime())])
        db.commit()
    return str()

@app.route('/<identifier>/poll')
def poll(identifier):
    if 'identifier' in session and session['identifier'] == identifier:
        identifier = int(identifier, 16)
        db = get_db()
        cur = db.execute('select text from messages where chat = ? and recver = ? order by time asc limit 1',
                [identifier, session['name']])
        entry = cur.fetchone()
        db.execute('delete from messages where chat = ? and recver = ? order by time asc limit 1',
                [identifier, session['name']])
        db.commit()
        if entry:
            return entry[0]
    return str()

@app.route('/<identifier>/leave', methods=['POST'])
def leave(identifier):
    if 'identifier' in session and session['identifier'] == identifier:
        identifier = int(identifier, 16)
        db = get_db()
        entry = db.execute('select full from chats where chat = ?', [identifier]).fetchone()
        if entry and not entry[0]:
            db.execute('delete from messages where chat = ?', [identifier])
        else:
            db.execute('delete from messages where chat = ? and recver = ?', [identifier, session['name']])
        db.execute('delete from chats where chat = ?', [identifier])
        db.execute('insert into messages values (?, ?, ?, ?, ?)',
                [identifier, session['name'], session['name'] ^ 1, '\x04', timegm(gmtime())])
        db.commit()
        session.pop('identifier')
        session.pop('name')
    return str()
