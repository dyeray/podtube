import os
from apiclient import discovery
from feedgen.feed import FeedGenerator
from pytube import YouTube
from pytube.exceptions import PytubeError
import dateutil.parser
import requests
import sys


def _create_youtube_client(http=None):
    return discovery.build('youtube', 'v3', developerKey=os.environ['youtube_developer_key'])


def get_feed(channel_id):
    service = _create_youtube_client()
    channel = service.channels().list(part='snippet', id=channel_id).execute()['items'][0]
    videos = service.search().list(part='snippet', channelId=channel_id, order='date',
                                   type='video', safeSearch='none').execute()
    fg = FeedGenerator()
    fg.load_extension('podcast')
    fg.title(channel['snippet']['title'])
    fg.description(channel['snippet']['description'])
    fg.link(href='https://www.youtube.com/channel/' + channel_id, rel='alternate')
    fg.image(channel['snippet']['thumbnails']['high']['url'])
    for video in videos['items']:
        try:
            video_url = YouTube("https://www.youtube.com/watch?v=" + video['id']['videoId']).filter('mp4')[0].url
        except PytubeError:
            continue
        fe = fg.add_entry()
        fe.id(video['id']['videoId'])
        fe.title(video['snippet']['title'])
        fe.description(video['snippet']['description'])
        fe.pubdate(dateutil.parser.parse(video['snippet']['publishedAt']))
        fe.podcast.itunes_image(video['snippet']['thumbnails']['high']['url'])
        video_info = requests.head(video_url)
        fe.enclosure(video_url, video_info.headers['Content-Length'], video_info.headers['Content-Type'])
    return fg.rss_str(pretty=True)


if __name__ == "__main__":
    print(get_feed(sys.argv[1]))