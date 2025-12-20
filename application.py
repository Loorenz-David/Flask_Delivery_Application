
from Delivery_app_BK import create_app
from Delivery_app_BK.socketio_instance import socketio

application = create_app("production")  

if __name__ == "__main__":
    socketio.run(application, host='0.0.0.0', port=8000, allow_unsafe_werkzeug=True)
