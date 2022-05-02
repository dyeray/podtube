import requests
from flask import Flask, request, Response, render_template, redirect, stream_with_context

from core.feed import render_feed
from core.options import GlobalOptions
from core.service.service_factory import ServiceFactory


app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html', host_url=request.host_url)


@app.route('/feed')
def feed():
    options = GlobalOptions(**request.args)
    feed_generator = ServiceFactory.create(options.service, request.args)
    return Response(
        render_feed(options.id, feed_generator, options, request.host_url),
        mimetype='application/rss+xml',
        content_type='text/xml'
    )


@app.route('/download')
def download():
    options = GlobalOptions(**request.args)
    url = ServiceFactory.create(options.service, request.args).get_item_url(options.id)
    if options.proxy_download:
        req = requests.get(url, stream=True)
        return Response(stream_with_context(req.iter_content()), content_type=req.headers['content-type'])
    else:
        return redirect(url, code=302)


@app.errorhandler(404)
def page_not_found(e):
    return 'Sorry, Nothing at this URL.', 404


@app.errorhandler(500)
def application_error(e):
    return 'Sorry, unexpected error: {}'.format(e), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
