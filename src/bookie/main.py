import logging
from bookie import app_generator


LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(logging.INFO)


app = app_generator.create_app()  # pylint: disable=invalid-name


if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.debug = False
    app.run(host="0.0.0.0", port=8000)
