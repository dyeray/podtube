from flask import Flask, request, Response, render_template
from feed import get_channel_feed, get_channel_id
app = Flask(__name__)


@app.route('/')
def index():
    channel_id = request.args.get('c')
    if channel_id:
        return Response(get_channel_feed(channel_id), mimetype='application/rss+xml',
                        content_type='text/xml')
    return render_template('index.html')


@app.route('/', methods=['POST'])
def getPersonById():
    user_input = request.form['user_input']
    channel_id = get_channel_id(user_input)
    feed_url = request.host_url + '?c=' + channel_id if channel_id else ''
    return feed_url


@app.errorhandler(404)
def page_not_found(e):
    return 'Sorry, Nothing at this URL.', 404


@app.errorhandler(500)
def application_error(e):
    return 'Sorry, unexpected error: {}'.format(e), 500


if __name__ == '__main__':
    app.run()
