
from django.template.loader import render_to_string
from django.contrib.syndication.views import Feed
from django.utils.feedgenerator import Rss201rev2Feed

import magic


class CustomRssFeedGenerator(Rss201rev2Feed):
    def root_attributes(self):
        attrs = super().root_attributes()
        attrs['xmlns:itunes'] = 'https://www.itunes.com/dtds/podcast-1.0.dtd'
        attrs['xmlns:googleplay'] = 'https://www.google.com/schemas/play-podcasts/1.0'
        attrs['xmlns:podcast'] = 'https://podcastindex.org/namespace/1.0'
        return attrs

    def add_root_elements(self, handler):
        super(CustomRssFeedGenerator, self).add_root_elements(handler)
        handler.startElement(u'image', {})
        handler.addQuickElement(u"url", self.feed['image_url'])
        handler.addQuickElement(u"title", self.feed['title'])
        handler.addQuickElement(u"link", self.feed['link'])
        handler.endElement(u'image')

        handler.addQuickElement('googleplay:owner', self.feed['author_email'])

        handler.startElement(u'itunes:owner', {})
        handler.addQuickElement(u"itunes:email", self.feed['author_email'])
        handler.endElement(u'itunes:owner')

        handler.startElement(u'podcast', {})
        handler.addQuickElement(u'locked', self.feed['feed_locked'])
        handler.endElement(u'podcast')

    def add_item_elements(self, handler, item):
        super(CustomRssFeedGenerator, self).add_item_elements(handler, item)
        handler.startElement(u'image', {})
        handler.addQuickElement(u"url", item['image_url'])
        handler.addQuickElement(u"title", item['title'])
        handler.addQuickElement(u"link", item['link'])
        handler.endElement(u'image')


class PodFeed(Feed):

    feed_type = CustomRssFeedGenerator
    description_template = 'podcastbird657/feed_item_description.html'

    def __init__(self, page):
        super(PodFeed, self).__init__()
        self.page = page
        self.title = page.title
        self.link = page.specific.index_page.full_url
        self.feed_url = page.full_url
        self.language = str(page.specific.language) if page.specific.language else 'en'

    def feed_extra_kwargs(self, item):
        return {
            'image_url': self.page.specific.image.get_rendition('min-1400x1400').file.url,
            'feed_locked': self.feed_locked(),
            }

    def item_extra_kwargs(self, item):
        return {'image_url': item.specific.image.get_rendition('min-1400x1400').file.url, }

    def description(self):
        rendered = render_to_string('podcastbird657/feed_description.html', { 'obj': self.page })
        return rendered

    def author_name(self):
        return self.page.owner.get_full_name()
    
    def author_email(self):
        return self.page.owner.email
    
    def author_link(self):
        try:
            return (self.page.specific.author_link) if self.page.specific.author_link else '/'
        except AttributeError:
            return '/'
    
    def categories(self):
        try:
            return [ tag.name for tag in self.page.specific.tags.all() ]
        except AttributeError:
            return []
    
    def feed_copyright(self):
        try:
            return self.page.specific.feed_copyright
        except AttributeError:
            return 'Copyright (c) ' + str(self.page.go_live_at.year) + ', ' + self.page.owner.get_full_name()

    def feed_locked(self):
        try:
            if self.page.specific.feed_locked:
                return 'yes'
            else:
                return 'no'
        except AttributeError:
            return 'no'

    def items(self):
        return self.page.specific.index_page.get_descendants().live(
            ).public().order_by('-first_published_at')

    def item_title(self, item):
        return item.title

    def item_link(self, item):
        return item.full_url

    def item_guid(self, item):
        return item.full_url

    item_guid_is_permalink = True

    def item_author_name(self, item):
        return item.owner.get_full_name()

    def item_author_email(self, item):
        return item.owner.email

    def item_author_link(self, item):
        try:
            return (item.specific.author_link) if item.specific.author_link else '/'
        except AttributeError:
            return '/'

    def item_enclosure_url(self, item):
        try:
            return item.get_site().root_url + item.specific.enclosure.file.url
        except:
            return

    def item_enclosure_length(self, item):
        try:
            return item.specific.enclosure_length
        except:
            return

    def item_enclosure_mime_type(self, item):
        try:
            if item.specific.enclosure_mime_type:
                return item.specific.enclosure_mime_type
            return magic.from_buffer(item.specific.enclosure.file.read(), mime=True)
        except:
            return

    def item_pubdate(self, item):
        if item.go_live_at:
            return item.go_live_at
        return item.first_published_at

    def item_updateddate(self, item):
        return item.last_published_at

    def item_categories(self, item):
        try:
            return [ tag.name for tag in item.specific.tags.all() ]
        except:
            return []
    
    def item_copyright(self, item):
        try:
            return item.specific.feed_copyright
        except AttributeError:
            return self.page.specific.feed_copyright
        except:
            return 'Copyright (c) ' + str(item.first_published_at.year) + ', ' + item.owner.get_full_name()
