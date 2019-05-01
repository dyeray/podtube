import os
import re
from functools import lru_cache

import dateutil.parser
from apiclient import discovery
from feedgen.feed import FeedGenerator

from model import PodcastFeed


@lru_cache(maxsize=1)
def _get_youtube_client():
    return discovery.build('youtube', 'v3', developerKey=os.environ['youtube_developer_key'])


def render_feed(feed: PodcastFeed):
    fg = FeedGenerator()
    fg.load_extension('podcast')
    fg.title(feed.title)
    fg.description(feed.description)
    fg.link(href=feed.link, rel='alternate')
    fg.image(feed.image)
    fg.id(feed.feed_id)

    for item in feed.items:
        fe = fg.add_entry()
        fe.id(item.item_id)
        fe.title(item.title)
        fe.description(item.description)
        fe.pubdate(item.date)
        fe.podcast.itunes_image(item.image)
        fe.enclosure(item.url, item.content_length, item.content_type)
    return fg.atom_str(pretty=True)


def get_channel_id(user_input):
    url_regex = r'((https?:\/\/)?www\.)?youtube\.com\/(channel|user)\/([\w-]+)'
    match = re.match(url_regex, user_input)
    service = _get_youtube_client()
    if match:
        if match.group(3) == 'user':
            user_id = match.group(4)
        else:
            channel_id = match.group(4)
    else:
        user_id = user_input
        channel_id = user_input
    try:
        if 'channel_id' in locals():
            return service.channels().list(
                part='snippet', id=channel_id).execute()['items'][0]['id']
    except IndexError:
        pass
    try:
        if 'user_id' in locals():
            return service.channels().list(
                part='snippet', forUsername=user_id).execute()['items'][0]['id']
    except IndexError:
        pass
    return None
