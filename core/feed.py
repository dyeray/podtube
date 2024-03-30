import warnings
from urllib.parse import urlencode

from pod2gen import Podcast, Episode, Media, NotSupportedByItunesWarning

from core.model import PodcastItem
from core.options import GlobalOptions
from core.plugin import Plugin


warnings.filterwarnings("ignore", category=NotSupportedByItunesWarning)
warnings.filterwarnings(
    "ignore",
    message="Size is set to 0. This should ONLY be done when there is no possible way to determine the media's size, like if the media is a stream.",
    category=UserWarning,
)


def render_feed(feed_id: str, plugin: Plugin, options: GlobalOptions, base_url: str):
    feed = plugin.get_feed(feed_id)
    podcast = Podcast(
        name=feed.title,
        description=feed.description,
        website=feed.link,
        image=str(options.icon) if options.icon else feed.image,
        explicit=False,
        episodes=[
            Episode(
                id=episode.item_id,
                title=episode.title,
                media=Media(
                    generate_url(episode, plugin, options, base_url),
                    episode.content_length,
                    type=episode.content_type,
                ),
                summary=episode.description,
                publication_date=episode.date,
                image=episode.image,
                link=episode.link,
            )
            for episode in feed.items
        ],
    )
    return podcast.rss_str()


def generate_url(
    episode: PodcastItem, plugin: Plugin, options: GlobalOptions, base_url: str
):
    if options.proxy_url:
        query_params = (
            options.model_dump(exclude_none=True)
            | plugin.options.model_dump(exclude_none=True)
            | {"id": episode.item_id}
        )
        return f"{base_url}download?" + urlencode(query_params)
    else:
        return plugin.get_item_url(episode.item_id)
