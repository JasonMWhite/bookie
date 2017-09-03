from sanic import Sanic
from sanic import response


app = Sanic(__name__)  # pylint: disable=invalid-name


@app.route('/')
async def hello(_):
    return response.html('<p><b>Hello, world!</p>')


if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host="0.0.0.0", port=8000)
