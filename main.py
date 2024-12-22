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

from core.auth import require_auth
from core.feed import render_feed
from core.migration import handle_legacy_redirect
from core.options import GlobalOptions, ServeOptions
from core.plugin.plugin_factory import PluginFactory
from core.storage.storage import Storage


load_dotenv()
app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html", host_url=request.host_url)


@app.route("/feed")
@require_auth
def feed():
    # Upgrade podtube v1 urls. Only for a limited time.
    redirect_resp = handle_legacy_redirect(request.args, "feed")
    if redirect_resp:
        return redirect_resp

    options = GlobalOptions(**request.args)
    feed_generator = PluginFactory.create(options.service, options.plugin, request.args)
    return Response(
        render_feed(options.id, feed_generator, options, request.host_url),
        mimetype="application/rss+xml",
        content_type="text/xml",
    )


@app.route("/download")
@require_auth
def download():
    # Upgrade podtube v1 urls. Only for a limited time.
    redirect_resp = handle_legacy_redirect(request.args, "download")
    if redirect_resp:
        return redirect_resp

    options = GlobalOptions(**request.args)
    url = PluginFactory.create(options.service, options.plugin, request.args).get_item_url(options.id)
    if options.proxy_download:
        req = httpx.get(url, stream=True)
        return Response(
            stream_with_context(req.iter_content()),
            content_type=req.headers["content-type"],
        )
    else:
        return redirect(url, code=302)


@app.route("/serve")
@require_auth
def serve():
    options = options = ServeOptions(**request.args)
    plugin = PluginFactory.create("", options.plugin, request.args)
    storage = Storage(plugin)
    shared_file = storage.serve(namespace=options.namespace, id=options.id)
    return Response(
        stream_with_context(generate_file(shared_file.file_handle)),
        content_type=shared_file.file_info.mimetype,
        headers={
            'Content-Disposition': f'attachment; filename="{shared_file.file_info.filename}"'
        },
    )

def generate_file(file_like_object):
    while chunk := file_like_object.read(8192):
        yield chunk


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
