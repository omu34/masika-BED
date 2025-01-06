from starter import create_app, socketio

app = create_app()

if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=3700, debug=True)
