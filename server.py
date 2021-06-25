import json
from time import time
import numpy as np
from flask import Flask, send_from_directory
import socketio
import eventlet, eventlet.wsgi

from ImgVector.retrieval import score as score_img
from ImgVector.retrieval import idx2id
from tfidf.tfidf import tfidf
score_ocr = tfidf.score

homepage_ids = [
    367277, 279612, 206899, 377061, 240277,
    347454, 326436, 383562, 390107, 333844,
    400765, 265198, 231704, 339998, 349362,
    399788, 279437, 338695, 321100, 381494]

#===============================================================================
# http server

app = Flask(__name__)

@app.route('/')
@app.route('/index.html')
def index():
    return send_from_directory('frontend', 'index.html')

@app.route('/eval')
def index_eval():
    return send_from_directory('frontend', 'eval.html')

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
    sio.emit('rank_list', homepage_ids)

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

    # scores
    scores_ocr = score_ocr(text_query) if len(text_query.strip()) else 0. # value in [0, 1] ?
    scores_img = score_img(img_query) if len(img_query) else 0. # value in [0, 1]

    scores = weight * scores_ocr \
           + (1 - weight) * scores_img

    # response
    if type(scores) == float and scores == 0.:
        response = homepage_ids
    else:
        indices = np.argsort(-scores)[:n_ranklist]
        response = idx2id[indices].tolist()
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
address = '0.0.0.0'
port = 80
green_socket = eventlet.listen((address, port))
print(f'Server is online at {address}:{port}')
print('=' * 80)

with open(log_file_name, 'a', encoding='utf-8') as log_file:
    log_file.write('=' * 10 + str(time()) + ': restart\n')
    # start wsgi server (blocking)
    eventlet.wsgi.server(green_socket, app, log_output=False)
