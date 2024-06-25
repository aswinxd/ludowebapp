from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO, join_room, leave_room, send
from pymongo import MongoClient

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

client = MongoClient('mongodb+srv://test:test@cluster0.q9llhnj.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client['ludo_game']
games_collection = db['games']

@app.route('/')
def index():
    return render_template('index.html')

@socketio.on('join')
def handle_join(data):
    room = data['room']
    join_room(room)
    send(f'{data["username"]} has entered the room.', room=room)

@socketio.on('leave')
def handle_leave(data):
    room = data['room']
    leave_room(room)
    send(f'{data["username"]} has left the room.', room=room)

@socketio.on('move')
def handle_move(data):
    game_id = data['game_id']
    games_collection.update_one({'_id': game_id}, {'$set': {'state': data['state']}})
    send(f'{data["username"]} made a move.', room=game_id)

if __name__ == '__main__':
    socketio.run(app)
