import os

import httpx
from dotenv import load_dotenv
from flask import (
    Flask,
    request,
    Response,
    render_template,
    redirect,
    stream_with_context,
)

from core.feed import render_feed
from core.options import GlobalOptions
from core.plugin.plugin_factory import PluginFactory


load_dotenv()
app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html", host_url=request.host_url)


@app.route("/feed")
def feed():
    options = GlobalOptions(**request.args)
    feed_generator = PluginFactory.create(options.service, request.args)
    return Response(
        render_feed(options.id, feed_generator, options, request.host_url),
        mimetype="application/rss+xml",
        content_type="text/xml",
    )


@app.route("/download")
def download():
    options = GlobalOptions(**request.args)
    url = PluginFactory.create(options.service, request.args).get_item_url(options.id)
    if options.proxy_download:
        req = httpx.get(url, stream=True)
        return Response(
            stream_with_context(req.iter_content()),
            content_type=req.headers["content-type"],
        )
    else:
        return redirect(url, code=302)


@app.route("/health-check")
def health_check():
    return "OK"


@app.errorhandler(404)
def page_not_found(e):
    return "Sorry, Nothing at this URL.", 404


@app.errorhandler(500)
def application_error(e):
    return "Sorry, unexpected error: {}".format(e), 500


if __name__ == "__main__":
    port = os.getenv("PODTUBE_PORT")
    app.run(host="0.0.0.0", port=int(port) if port and port.isdigit() else 8080)
