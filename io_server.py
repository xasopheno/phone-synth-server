import socketio
import eventlet
from flask import Flask
import random
import json

sio = socketio.Server(logger=True)
app = Flask(__name__)

clients = []


class Counter:
    def __init__(self):
        self.count = 0

    def inc(self):
        self.count += 1


counter = Counter()


@sio.on('connect')
def connect(sid, environ):
    print('client_connect', sid)
    clients.append(sid)
    sio.emit(
        'connected_to_server',
        {'message': 'Connected', 'count': counter.count},
        room=sid
    )

    counter.count += 1


@sio.on('disconnect')
def disconnect(sid):
    clients.remove(sid)


def prepare_payload(array_freqs):
    payload = {
        'freqs': array_freqs,
        'vol': 100
    }
    return payload


@sio.on('freq_change')
def freq_change(sid, data):
    sio.emit('freq', data)


@sio.on('echo')
def message(sid, data):
    print('echo')
    rand = random.randint(100, 1000)
    payload = prepare_payload([rand, rand + 100, rand + 200, rand + 300])
    print(payload)

    sio.emit('freq', payload)


app = socketio.Middleware(sio, app)

if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('localhost', 9876)), app)
