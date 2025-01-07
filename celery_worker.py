from starter import create_app, celery

# Create the Flask app and integrate Celery
flask_app = create_app()

# Update Celery configuration with Flask app configuration
celery.conf.update(flask_app.config)

# Optional: Allow Celery tasks to access the Flask app context
# This ensures tasks have access to the app's database, configuration, etc.
TaskBase = celery.Task

class ContextTask(TaskBase):
    abstract = True

    def __call__(self, *args, **kwargs):
        with flask_app.app_context():
            return TaskBase.__call__(self, *args, **kwargs)

celery.Task = ContextTask
