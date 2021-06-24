import json
from time import time
from flask import Flask, send_from_directory
import socketio
import eventlet, eventlet.wsgi

from retrieval import retrieve

#===============================================================================
# http server

app = Flask(__name__)

@app.route('/')
def index():
    return send_from_directory('frontend', 'index.html')

@app.route('/css/<string:path>')
def send_css(path):
    return send_from_directory('frontend/css', path)

@app.route('/js/<string:path>')
def send_js(path):
    return send_from_directory('frontend/js', path)

@app.route('/img/<string:path>')
def send_img(path):
    return send_from_directory('frontend/img', path)

@app.route('/img_db/<string:path>')
def send_img_db(path):
    return send_from_directory('images/memes_tw/class0', path)

#===============================================================================
# socket

sio = socketio.Server()
app = socketio.WSGIApp(sio, app)

@sio.on('connect')
def connect_cb(sid, environ):
    sio.emit('rank_list', [
        216711, 118624, 385215, 377061, 285079,
        286972, 387652, 401473, 396483, 299857,
        400765, 240988, 406519, 354556, 307092,
        410957, 209286, 334331, 229512, 385606]) # initial list

    json_str = json.dumps({
        'time': time(),
        'sid': sid,
        'event': 'connect'}, ensure_ascii=False)
    log_file.write(json_str + '\n')
    print(f'{sid}: connect')

@sio.on('disconnect')
def disconnect_cb(sid):
    json_str = json.dumps({
        'time': time(),
        'sid': sid,
        'event': 'disconnect'}, ensure_ascii=False)
    log_file.write(json_str + '\n')
    print(f'{sid}: disconnect')

@sio.on('query')
def query_cb(sid, query):
    img_query = query['img_query']
    text_query = query['text_query']
    n_ranklist = query['n_ranklist']
    weight = query['weight']

    response = retrieve(img_query, n_ranklist)
    sio.emit('rank_list', response)

    json_str = json.dumps({
        'time': time(),
        'sid': sid,
        'event': 'query',
        'query': query,
        'response': response}, ensure_ascii=False)
    log_file.write(json_str + '\n')
    print(f'{sid}: query={query}')

#===============================================================================
# start server

log_file_name = 'server_log.txt'
address = '127.0.0.1'
port = 8080
green_socket = eventlet.listen((address, port))
print(f'Server is online at {address}:{port}')
print('=' * 80)

with open(log_file_name, 'a', encoding='utf-8') as log_file:
    log_file.write('=' * 10 + str(time()) + ': restart\n')
    # start wsgi server (blocking)
    eventlet.wsgi.server(green_socket, app, log_output=False)