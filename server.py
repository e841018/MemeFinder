import json
from time import time
import numpy as np
from flask import Flask, send_from_directory, send_file
import socketio
import eventlet, eventlet.wsgi

import sys
if sys.platform != 'win32':
    import resource
    resource.setrlimit(resource.RLIMIT_NOFILE, (65536, 65536))

# preallocate resources
import os, io
from tqdm import tqdm
img_dict = {}
img_dir = 'images/memes_tw/class0'
for path in tqdm(os.listdir(img_dir)):
    with open(os.path.join(img_dir, path), 'rb') as f:
        img_dict[path] = f.read()

from quiz import sample_quiz
from ImgVector.retrieval import idx2id
from ImgVector.retrieval import score as score_img
from tfidf.tfidf import tfidf
score_text = tfidf.score

homepage_ids = [
    367277, 279612, 206899, 377061, 240277,
    347454, 326436, 383562, 390107, 333844,
    400765, 265198, 231704, 339998, 349362,
    399788, 279437, 338695, 321100, 381494]

max_user = 10
sid_pool = set() # allowed access

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
    # return send_from_directory('images/memes_tw/class0', path)
    mem = io.BytesIO()
    mem.write(img_dict[path])
    mem.seek(0)
    return send_file(mem, mimetype='image/jpeg')

#===============================================================================
# socket

sio = socketio.Server()
app = socketio.WSGIApp(sio, app)

@sio.on('connect')
def connect_cb(sid, environ):
    if len(sid_pool) >= max_user:
        sio.emit('overload', room=sid)
        print(f'{sid}: too much users, forbidden')
        return
    sid_pool.add(sid)

    sio.emit('rank_list', homepage_ids, room=sid)
    sio.emit('sid', sid, room=sid)

    json_str = json.dumps({
        'time': time(),
        'sid': sid,
        'event': 'connect'}, ensure_ascii=False)
    log_file.write(json_str + '\n')
    print(f'{sid}: connect, {len(sid_pool)} active connections')

@sio.on('disconnect')
def disconnect_cb(sid):
    if sid in sid_pool:
        sid_pool.remove(sid)

    json_str = json.dumps({
        'time': time(),
        'sid': sid,
        'event': 'disconnect'}, ensure_ascii=False)
    log_file.write(json_str + '\n')
    print(f'{sid}: disconnect')

@sio.on('query')
def query_cb(sid, query):
    if sid not in sid_pool:
        return

    img_query = query['img_query']
    text_query = query['text_query']
    n_ranklist = query['n_ranklist']
    weight = query['weight']
    disable_pseudo_label = 'set' in query and query['set'] == 1 # UI: Set 2

    # scores
    scores_ocr, scores_tag, scores_all = score_text(text_query) # value in [0, 1] ?
    scores_img = score_img(img_query) if len(img_query) else 0. # value in [0, 1]

    if disable_pseudo_label:
        scores = weight * scores_ocr \
            + (1 - weight) * scores_img
    else:
        scores = weight * scores_all \
            + (1 - weight) * scores_img

    # response
    if np.all(scores == 0):
        response = []
    else:
        indices = np.argsort(-scores)[:n_ranklist]
        response = idx2id[indices].tolist()
    sio.emit('rank_list', response, room=sid)
    json_str = json.dumps({
        'time': time(),
        'sid': sid,
        'event': 'query',
        'query': query,
        'response': response}, ensure_ascii=False)
    log_file.write(json_str + '\n')
    print(f'{sid}: query={query}')

@sio.on('start_quiz')
def start_eval_cb(sid):
    if sid not in sid_pool:
        return

    quiz = sample_quiz(20)
    sio.emit('quiz', quiz, room=sid)
    json_str = json.dumps({
        'time': time(),
        'sid': sid,
        'event': 'start_quiz',
        'quiz': quiz}, ensure_ascii=False)
    log_file.write(json_str + '\n')
    print(f'{sid}: quiz=[{quiz[0]}, {quiz[1]}, ...]')

@sio.on('submit')
def submit_cb(sid, data):
    json_str = json.dumps({
        'time': time(),
        'sid': sid,
        'event': 'submit',
        'submission': data}, ensure_ascii=False)
    log_file.write(json_str + '\n')
    print(f'{sid}: submit question {data[0]}: id={data[1]}')

# @sio.on('finish')
# def finish_cb(sid, data):
#     json_str = json.dumps({
#         'time': time(),
#         'sid': sid,
#         'event': 'finish',
#         'contact': data}, ensure_ascii=False)
#     log_file.write(json_str + '\n')
#     print(f'{sid}: finished. contact: {data}')

#===============================================================================
# start server

log_file_name = 'server_log.txt'
address = '0.0.0.0'
port = 8080
green_socket = eventlet.listen((address, port))
print(f'Server is online at {address}:{port}')
print('=' * 80)

with open(log_file_name, 'a', encoding='utf-8') as log_file:
    log_file.write('=' * 10 + str(time()) + ': restart\n')
    # start wsgi server (blocking)
    eventlet.wsgi.server(green_socket, app, log_output=False)
