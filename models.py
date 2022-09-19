import uuid

from django.db import models
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator

from wagtail.core.models import Page
from wagtail.core.fields import RichTextField, StreamField
from wagtail.core import blocks

from wagtail.contrib.settings.models import BaseSiteSetting, register_setting

from wagtail.admin.edit_handlers import (FieldPanel, StreamFieldPanel, PageChooserPanel)

from wagtail.search import index

from wagtail.images.edit_handlers import ImageChooserPanel

from wagtailmedia.edit_handlers import MediaChooserPanel

from modelcluster.fields import ParentalKey
from modelcluster.contrib.taggit import ClusterTaggableManager

from taggit.models import TaggedItemBase

from .feeds import PodFeed


@register_setting
class PodcastSettings(BaseSiteSetting):
    logo = models.ForeignKey(
        'wagtailimages.Image',
        blank=True, null=True,
        on_delete=models.SET_NULL,
        related_name='+'
        )

    panels = [
        ImageChooserPanel('logo'),
    ]


class BirdMixin(models.Model):
    image = models.ForeignKey(
        'wagtailimages.Image',
        blank=True, null=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    intro = RichTextField(
        blank=True, null=True,
        features=[
            'h2', 'h3', 'h4',
            'bold', 'italic',
            'superscript', 'subscript', 'strikethrough',
            'ol', 'ul', 'hr',
            'link', 'document-link', 'blockquote']
            )

    show_breadcrumbs = models.BooleanField(default=False)
    show_cover = models.BooleanField(default=False)
    show_date = models.BooleanField(default=False)
    exclude_from_sitemap = models.BooleanField(default=False)

    class Meta:
        abstract = True

    search_fields = [
        index.SearchField('intro'),
    ]
    content_panels = [
        FieldPanel('owner'),
        ImageChooserPanel('image'),
        FieldPanel('intro', classname="full"),
    ]
    settings_panels = [
        FieldPanel('show_breadcrumbs'),
        FieldPanel('show_cover'),
        FieldPanel('show_date'),
        FieldPanel('exclude_from_sitemap'),
    ]


class PodEpisodeBirdPageTag(TaggedItemBase):
    content_object = ParentalKey(
        'PodEpisodeBirdPage',
        on_delete=models.CASCADE,
        related_name='tagged_items')


class PodEpisodeBirdPage(Page, BirdMixin):
    body = StreamField([
        ('paragraph', blocks.RichTextBlock(
            required=False, null=True,
            features=[
                'h2', 'h3', 'h4',
                'bold', 'italic',
                'superscript', 'subscript', 'strikethrough',
                'ol', 'ul', 'hr',
                'link', 'document-link',
                'blockquote', 'embed', 'image'])),
    ], blank=True, null=True)
    enclosure = models.ForeignKey(
        'wagtailmedia.Media',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    enclosure_length = models.IntegerField(blank=True, null=True)
    enclosure_mime_type = models.CharField(max_length=50, blank=True, null=True)
    explicit = models.BooleanField(default=False)
    tags = ClusterTaggableManager(through=PodEpisodeBirdPageTag, blank=True)
    search_fields = Page.search_fields + BirdMixin.search_fields + [
        index.SearchField('body'),
    ]
    content_panels = Page.content_panels + BirdMixin.content_panels + [
        StreamFieldPanel('body'),
        MediaChooserPanel('enclosure'),
        FieldPanel('enclosure_length'),
        FieldPanel('enclosure_mime_type'),
        ]
    promote_panels = Page.promote_panels + [
        FieldPanel('tags'),
        ]
    settings_panels = Page.settings_panels + BirdMixin.settings_panels + [
        FieldPanel('explicit'),
        ]

    def get_sitemap_urls(self, request=None):
        if self.exclude_from_sitemap:
            return []
        else:
            return super(PodEpisodeBirdPage, self).get_sitemap_urls(
                request=request)


class PodCastBirdPageTag(TaggedItemBase):
    content_object = ParentalKey(
        'PodCastBirdPage',
        on_delete=models.CASCADE,
        related_name='tagged_items')


class PodCastBirdPage(Page, BirdMixin):
    guid = models.UUIDField(default=uuid.uuid4, editable=False)
    language = models.CharField(max_length=5, blank=True, null=True)
    author_link = models.URLField(blank=True, null=True)
    feed_copyright = models.CharField(max_length=128, blank=True, null=True)
    feed_locked = models.BooleanField(default=False)
    explicit = models.BooleanField(default=False)

    tags = ClusterTaggableManager(through=PodCastBirdPageTag, blank=True)
    
    search_fields = Page.search_fields + BirdMixin.search_fields
    content_panels = Page.content_panels + BirdMixin.content_panels + [
        FieldPanel('language'),
        FieldPanel('author_link'),
        FieldPanel('feed_copyright'),
    ]
    promote_panels = Page.promote_panels + [FieldPanel('tags'), ]
    settings_panels = Page.settings_panels + [
        FieldPanel('show_breadcrumbs'),
        FieldPanel('show_cover'),
        FieldPanel('exclude_from_sitemap'),
        FieldPanel('feed_locked'),
        FieldPanel('explicit'),
    ]

    def get_sitemap_urls(self, request=None):
        if self.exclude_from_sitemap:
            return []
        else:
            return super(PodCastBirdPage, self).get_sitemap_urls(
                request=request)

    def get_context(self, request):
        context = super().get_context(request)
        all_posts = Page.objects.live().public().exclude(
            pk=self.pk).filter(
                content_type__model='podepisodebirdpage').order_by('-go_live_at').distinct()
        paginator = Paginator(all_posts, 10)
        page = request.GET.get("page", 1)
        try:
            posts = paginator.page(page)
        except PageNotAnInteger:
            posts = paginator.page(1)
        except EmptyPage:
            posts = paginator.page(paginator.num_pages)
        context['posts'] = posts
        return context


class PodCastFeedBirdPage(Page):
    index_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
    )
    exclude_from_sitemap = models.BooleanField(default=False)

    content_panels = Page.content_panels + [PageChooserPanel('index_page'),]
    settings_panels = Page.settings_panels + [
        FieldPanel('exclude_from_sitemap'),
    ]
    
    def serve(self, request):
        return PodFeed(self)(request)

    def get_sitemap_urls(self, request=None):
        if self.exclude_from_sitemap:
            return []
        else:
            return super(PodCastFeedBirdPage, self).get_sitemap_urls(request=request)
