from Starter import create_app, socketio

app = create_app()

if __name__ == '__main__':
    # start_background_listener()  # Start listening in the background
    socketio.run(app, host="0.0.0.0", port=3700, debug=True)
