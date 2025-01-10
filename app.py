from api import create_app, socketio,celery

app = create_app()
celery.conf.update(app.config)
if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port=10000, debug=True)
