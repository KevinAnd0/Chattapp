from chat import create_app
from flask_socketio import SocketIO
from chat.database import DataBase
import base64

app = create_app()
socket = SocketIO(app)

@socket.on('connecting')
def connect(json, methods=['GET', 'POST']):
    print('received my event: ' + str(json))
    db = DataBase()
    db.update_user(online=True, socket_id=json['socket_id'], username=json['user'])
    db.commit()
    
@socket.on('message')
def message(json, methods=['GET', 'POST']):
    db = DataBase()
    sender = db.get_one_user(json['sender'])[0]
    receiver = db.get_one_user(json['user2'])[0]
    msg = json['message']
    time = json['time']
    db.create_message(message=msg, sender=sender['username'], time=time)
    db.commit()
    socket.emit('response', json, to=receiver['socket_id'])

@socket.on('image')
def image(image, methods=['GET', 'POST']):
    socket.emit('receive image', {'data': base64.encodebytes(image)})



if __name__ == "__main__":
    socket.run(app, debug=True, port=8000)
