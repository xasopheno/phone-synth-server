import mido
import re
from socketIO_client import SocketIO, LoggingNamespace
import json

ports = mido.get_input_names()
print(ports)
socket = SocketIO('phone-synth-server.herokuapp.com', 80, LoggingNamespace)
# socket = SocketIO('localhost', 9876, LoggingNamespace)

midi_array = []


def midi_to_hertz(midi):
    if midi == 0:
        return 0
    f = 2**((midi-69)/12) * 440
    return f


def send_to_socket(freq_array, vol):
    data = json.dumps({'freq': freq_array, 'vol': vol})
    socket.emit('freq_change', data)


def handle_event(event):
    note_on_regex = re.compile('(?:note_on)')
    note_off_regex = re.compile('(?:note_off)')

    if note_on_regex.match(str(event)):
        note_on(event)

    if note_off_regex.match(str(event)):
        note_off(event)


def note_on(event):
    note_regex = re.compile('(note=.[0-9])')
    midi_num_regex = re.compile('([0-9]+)')
    note = note_regex.search(str(event))[0]
    midi = midi_num_regex.search((str(note)))[0]
    midi_array.append(int(midi))
    # print(midi_array)


def note_off(event):
    note_regex = re.compile('(note=.[0-9])')
    midi_num_regex = re.compile('([0-9]+)')
    note = note_regex.search(str(event))[0]
    midi = midi_num_regex.search((str(note)))[0]
    midi_array.remove(int(midi))
    # print(midi_array, midi)


with mido.open_input('microKEY-25 KEYBOARD') as inport:
    for event in inport:
        handle_event(event)
        midi_array = list(map(int, midi_array))
        freq_array = list(map(midi_to_hertz, midi_array))
        print(list(freq_array))
        if len(freq_array) == 0:
            freq_array = [0]
        send_to_socket(freq_array, 100)
