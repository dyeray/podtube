from feedgen.feed import FeedGenerator

from core.model import PodcastFeed


def render_feed(feed: PodcastFeed, format: str):
    fg = FeedGenerator()
    fg.load_extension('podcast')
    fg.title(feed.title)
    fg.description(feed.description)
    fg.link(href=feed.link, rel='alternate')
    fg.image(feed.image)
    fg.id(feed.feed_id)
    for item in reversed(feed.items):
        fe = fg.add_entry()
        fe.id(item.item_id)
        fe.title(item.title)
        fe.description(item.description)
        fe.pubDate(item.date)
        fe.podcast.itunes_image(item.image)
        fe.enclosure(item.url, item.content_length, item.content_type)
    return fg.rss_str(pretty=True) if format == 'rss' else fg.atom_str(pretty=True)
