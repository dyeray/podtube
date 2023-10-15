from urllib.parse import urlencode

from pod2gen import Podcast, Episode, Media

from core.model import PodcastItem
from core.options import GlobalOptions
from core.plugin import Plugin


def render_feed(feed_id: str, plugin: Plugin, options: GlobalOptions, base_url: str):
    feed = plugin.get_feed(feed_id)
    podcast = Podcast(
        name=feed.title,
        description=feed.description,
        website=feed.link,
        image=options.icon or feed.image,
        explicit=False,
        episodes=[
            Episode(
                id=episode.item_id,
                title=episode.title,
                media=Media(generate_url(episode, plugin, options, base_url), episode.content_length, type=episode.content_type),
                summary=episode.description.replace("\n", "<br>") if episode.description and options.html_newlines else episode.description,
                publication_date=episode.date,
                image=episode.image,
                link=episode.link
            ) for episode in feed.items
        ]
    )
    return podcast.rss_str()


def generate_url(episode: PodcastItem, plugin: Plugin, options: GlobalOptions, base_url: str):
    if options.proxy_url:
        return f'{base_url}download?' + urlencode(options.dict() | plugin.options.dict() | {'id': episode.item_id})
    else:
        return plugin.get_item_url(episode.item_id)
