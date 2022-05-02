import re
from typing import List

import dateparser
import requests
from parsel import Selector, SelectorList

from core.model import PodcastFeed, PodcastItem
from core.scrape_utils import clean, clean_image_url
from core.plugin.plugin import Plugin


class PluginImpl(Plugin):
    def get_feed(self, feed_id):
        """Calculates and returns the subscribable feed."""
        url = f'https://www.ivoox.com/{feed_id}.html'
        response = requests.get(url)
        sel = Selector(response.text)
        videos = sel.css('.modulo-type-episodio')
        return PodcastFeed(
            feed_id=feed_id,
            title=clean(sel.css('#list_title_new::text').get()),
            description=clean(sel.css('.overview::text').get()),
            link=url,
            image=sel.css("meta[property='og:image']::attr(content)").get(),
            items=self._get_items(videos)
        )

    def get_item_url(self, item_id):
        """Calculates the downloadable url of an item in the feed."""
        match = re.match(r'.*(_\d+_\d)', item_id)
        podcast_id = match and match.group(1)[1:]
        return f'http://www.ivoox.com/listen_mn_{podcast_id}.m4a?internal=HTML5'

    def _get_items(self, items: SelectorList) -> List[PodcastItem]:
        return [self._get_item(item) for item in items]

    def _get_item(self, item: Selector) -> PodcastItem:
        url = item.css('.title-wrapper a::attr(href)').get()
        re_item_id = re.match(r'https?://www\.ivoox\.com/([-_\w\d]+)\.html', url)
        item_id = re_item_id and re_item_id.group(1)
        date = dateparser.parse(
            item.css('.action .date::attr(title)').get(),
            settings={'RETURN_AS_TIMEZONE_AWARE': True, 'TO_TIMEZONE': 'UTC'}
        )
        return PodcastItem(
            item_id=item_id,
            title=item.css('.title-wrapper a::attr(title)').get(),
            description=item.css('.audio-description button::attr(data-content)').get() or '',
            date=date,
            image=self._get_episode_image(item),
            content_type='audio/mp4',
        )

    def _get_episode_image(self, item: Selector):
        image_url = item.css('a img::attr(data-src)').get()
        return clean_image_url(image_url)
