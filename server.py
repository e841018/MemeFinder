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
    print('connected:', sid)
    sio.emit('rank_list', [321100, 377618, 267348, 375601]) # initial list

@sio.on('disconnect')
def disconnect_cb(sid):
    print('disconnected:', sid)

@sio.on('dev')
def dev_cb(sid, data):
    print('dev received:', data)

@sio.on('query')
def query_cb(sid, data):
    print('query received:', data)
    fb_list, text_query, n_ranklist = data
    ids = retrieve(fb_list, n_ranklist)
    sio.emit('rank_list', ids)

#===============================================================================
# start server

green_socket = eventlet.listen(('127.0.0.1', 8080))
# start wsgi server (blocking)
print('Server is online!')
print('=' * 80)
eventlet.wsgi.server(green_socket, app, log_output=False)