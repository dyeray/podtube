import os
from apiclient import discovery
from feedgen.feed import FeedGenerator
import youtube_dl
import dateutil.parser
import requests
import sys
import re


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
    ytdl = youtube_dl.YoutubeDL()
    for video in videos['items']:
        try:
            video_url = ytdl.extract_info('https://www.youtube.com/watch?v=faycTt-FtfU&feature=youtu.be&t=16m39s', download=False)['url']
        except Exception:
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


def get_channel_id(user_input):
    url_regex = r'((https?:\/\/)?www\.)?youtube\.com\/(channel|user)\/(\w+)'
    match = re.match(url_regex, user_input)
    service = _create_youtube_client()
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
            return service.channels().list(part='snippet', id=channel_id).execute()['items'][0]['id']
    except IndexError:
        pass
    try:
        if 'user_id' in locals():
            return service.channels().list(part='snippet', forUsername=user_id).execute()['items'][0]['id']
    except IndexError:
        pass
    return None 


if __name__ == "__main__":
    if sys.argv[1] == 'id':
        print(get_channel_id(sys.argv[2]))
    elif sys.argv[1] == 'content':
        print(get_feed(sys.argv[2]))
    else:
        print('ERROR: Call it passing "id <user/channel/url>" to get channel id, or "content <channel_id>" to get feed content')
