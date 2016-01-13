from flask import Flask, request, Response
from feed import get_feed
app = Flask(__name__)


@app.route('/')
def hello():
    channel_id = request.args.get('c')
    if channel_id:
        return get_feed(channel_id), 200
    return Response('?c=<channel_id>', mimetype='application/rss+xml')


@app.errorhandler(404)
def page_not_found(e):
    return 'Sorry, Nothing at this URL.', 404


@app.errorhandler(500)
def application_error(e):
    return 'Sorry, unexpected error: {}'.format(e), 500


if __name__ == '__main__':
    app.run()