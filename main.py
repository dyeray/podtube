import httpx
from dotenv import load_dotenv
from flask import (
    Flask,
    Response,
    redirect,
    render_template,
    request,
    stream_with_context,
)
from werkzeug.utils import secure_filename

from core.auth import require_auth
from core.config import Config
from core.feed import render_feed
from core.options import GlobalOptions
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
    options = GlobalOptions(**request.args)
    feed_generator = PluginFactory.create(options.service, options.plugin, request.args)
    return Response(
        render_feed(options.id, feed_generator, options, request.host_url),
        mimetype="application/rss+xml",
        content_type="text/xml",
    )


@app.route("/download", methods=["HEAD"])
@require_auth
def download_head():
    options = GlobalOptions(**request.args)
    plugin = PluginFactory.create(options.service, options.plugin, request.args)
    return Response(status=200, headers=plugin.peek(options.id))


@app.route("/download", methods=["GET"])
@require_auth
def download():
    options = GlobalOptions(**request.args)
    plugin = PluginFactory.create(options.service, options.plugin, request.args)
    if Config.is_filesystem_mode_enabled(plugin) and options.storage:
        storage = Storage(plugin)
        return _serve_with_storage(options, plugin, storage)
    if options.proxy_download:
        url = plugin.get_item_url(options.id)
        req = httpx.get(url, stream=True)
        return Response(
            stream_with_context(req.iter_content()),
            content_type=req.headers["content-type"],
        )
    else:
        return redirect(plugin.get_item_url(options.id), code=302)


def _serve_with_storage(options, plugin, storage):
    """Serve from storage if available, otherwise trigger a background download."""
    namespace = options.feed_id
    item_id = options.id
    if not namespace:
        return Response("Missing feed_id parameter", status=400)

    file_id = storage.find_stored_id(namespace, item_id)
    if file_id is not None:
        shared_file = storage.serve(namespace, file_id)
        return _stream_shared_file(shared_file)

    if storage.is_downloading(namespace, item_id):
        return Response(status=202, headers={"Retry-After": "30"})

    download_fn = plugin.get_download_fn(item_id)
    if download_fn:
        storage.request_download(namespace, item_id, download_fn)
        return Response(status=202, headers={"Retry-After": "30"})

    return redirect(plugin.get_item_url(options.id), code=302)


def _stream_shared_file(shared_file):
    """Stream a SharedFile as an HTTP response."""
    safe_name = secure_filename(shared_file.file_info.filename) or "download"
    resp = Response(
        stream_with_context(generate_file(shared_file.file_handle)),
        content_type=shared_file.file_info.mimetype or "application/octet-stream",
        headers={
            "Content-Disposition": f'attachment; filename="{safe_name}"',
            "Content-Length": str(shared_file.file_info.size),
        },
    )
    resp.call_on_close(shared_file.close)
    return resp


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
    app.logger.exception("Unhandled error: %s", e)
    return "Sorry, unexpected error.", 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=Config.get_port())
