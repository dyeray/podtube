from urllib.parse import urlencode

from feedgen.feed import FeedGenerator

from core.model import PodcastItem
from core.options import GlobalOptions
from core.service import Service


def render_feed(feed_id: str, services: list[Service], options: GlobalOptions, base_url: str):
    service = services[0]
    feed = service.get_feed(feed_id)
    fg = FeedGenerator()
    fg.load_extension('podcast')
    fg.title(feed.title)
    fg.description(feed.description)
    fg.link(href=feed.link, rel='alternate')
    fg.image(options.icon or feed.image)
    fg.id(feed.feed_id)
    for item in reversed(feed.items):
        fe = fg.add_entry()
        fe.id(item.item_id)
        fe.title(item.title)
        fe.description(item.description)
        fe.pubDate(item.date)
        fe.podcast.itunes_image(item.image)
        fe.enclosure(generate_url(item, service, options, base_url), item.content_length, item.content_type)
    return fg.rss_str(pretty=True) if options.format == 'rss' else fg.atom_str(pretty=True)


def generate_url(episode: PodcastItem, service: Service, options: GlobalOptions, base_url: str):
    if options.proxy_url:
        return f'{base_url}download?' + urlencode(options.dict() | service.options.dict() | {'id': episode.item_id})
    else:
        return service.get_item_url(episode.item_id)
