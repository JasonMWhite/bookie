import logging

from sanic import Sanic
from sanic import response


app = Sanic(__name__)


@app.route('/')
async def hello(request):
    return response.html('<p><b>Hello, world!</p>')


# @app.errorhandler(500)
# def server_error(e):
#     logging.exception('An error occurred during a request.')
#     return """
#     An internal error occurred: <pre>{}</pre>
#     See logs for full stacktrace.
#     """.format(e), 500


if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host="0.0.0.0", port=8000)
