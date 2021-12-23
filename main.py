import requests
from flask import Flask, request, Response, render_template, redirect, stream_with_context

from feed import render_feed
from plugins.plugin_factory import PluginFactory


app = Flask(__name__)


@app.route('/')
def index():
    feed_id = request.args.get('c')
    format = request.args.get('format', 'rss')
    if not feed_id:
        return render_template('index.html')
    service = request.args.get('s')
    feed_object = PluginFactory.create(service).get_feed(feed_id, request.host_url, request.args)
    return Response(
        render_feed(feed_object, format),
        mimetype='application/rss+xml',
        content_type='text/xml'
    )


@app.route('/download')
def download():
    item_id = request.args.get('id')
    service = request.args.get('s')
    proxy = request.args.get('proxy') or False
    url = PluginFactory.create(service).get_item_url(item_id)
    if proxy:
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
