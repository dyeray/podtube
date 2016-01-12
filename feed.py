import os
from apiclient import discovery
from feedgen.feed import FeedGenerator
from pytube import YouTube


def _create_youtube_client(http=None):
    return discovery.build('youtube', 'v3', developerKey=os.environ['youtube_developer_key'])


def get_feed(channel_id):
    service = _create_youtube_client()
    channel = service.channels().list(part='snippet', id=channel_id).execute()['items'][0]
    videos = service.search().list(part='snippet', channelId=channel_id).execute()
    fg = FeedGenerator()
    fg.load_extension('podcast')
    fg.title(channel['snippet']['title'])
    fg.description(channel['snippet']['description'])
    fg.link(href='https://www.youtube.com/channel/' + channel_id, rel='alternate')
    for video in videos['items']:
        fe = fg.add_entry()
        fe.id(video['id']['videoId'])
        fe.title(video['snippet']['title'])
        fe.description(video['snippet']['description'])
        fe.enclosure(YouTube("https://www.youtube.com/watch?v=" + video['id']['videoId']).filter('mp4')[0].url, 0, 'video/mpeg')
    return fg.rss_str(pretty=True)
