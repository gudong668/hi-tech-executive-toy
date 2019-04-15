import json

from flask import Flask,request
from geventwebsocket.websocket import WebSocket
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler

ws_serv = Flask(__name__)

user_socket_dict = {}

@ws_serv.route("/toy/<toy_id>")
def toy(toy_id):
    user_socket = request.environ.get("wsgi.websocket") # type:WebSocket
    if user_socket:
        user_socket_dict[toy_id] = user_socket
        print(len(user_socket_dict),user_socket_dict)

    while True:
        user_msg = user_socket.receive()
        if not user_msg:
            return "断了!友尽！"
        print(user_msg, type(user_msg))  # {to_user:toy001,music:"uuid4().mp3"}
        user_msg_dict = json.loads(user_msg)
        to_user = user_msg_dict.get("to_user")
        to_user_socket = user_socket_dict.get(to_user)
        try:
            to_user_socket.send(user_msg)
        except:
            continue


@ws_serv.route("/app/<app_id>")
def app(app_id):
    user_socket = request.environ.get("wsgi.websocket") # type:WebSocket
    if user_socket:
        user_socket_dict[app_id] = user_socket
        print(len(user_socket_dict), user_socket_dict)
    while True:
        user_msg = user_socket.receive()
        if not user_msg:
            return "断了!友尽！"
        print(user_msg,type(user_msg)) # {to_user:toy001,music:"uuid4().mp3"}
        user_msg_dict = json.loads(user_msg)
        to_user = user_msg_dict.get("to_user")
        to_user_socket = user_socket_dict.get(to_user)

        try:
            to_user_socket.send(user_msg)
        except:
            continue




if __name__ == '__main__':
    http_serv = WSGIServer(("0.0.0.0",9528),application=ws_serv,handler_class=WebSocketHandler)
    http_serv.serve_forever()