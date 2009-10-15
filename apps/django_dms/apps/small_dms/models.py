#!/usr/bin/env python
#-*- coding:utf-8 -*-

from django.db import models
from django_dms.models import DocumentBase
from tribes.models import Tribe
from django.utils.translation import ugettext_lazy as _
from tagging.fields import TagField
from django.contrib.auth.models import User




class Document(DocumentBase):
    """ Basic document entry, with a selected metadata.
    """
    title           = models.CharField(_('title'), max_length=150, default="")
    slug            = models.SlugField(_('slug'))
    summary         = models.TextField(_('abstract / summary'), default="", blank=True)
    date_created    = models.DateTimeField(_("created"), blank=True)
    tribe           = models.ForeignKey(Tribe, related_name="documents", verbose_name=_('tribe'))
    tags            = TagField()
    uploader        = models.ForeignKey(User, related_name="documents", verbose_name=_('uploader'))   

    GRADES = (
            (-3, '-3'),
            (00, '00'),
            (02, '02'),
            (4 , '04'),
            (7 , '07'),
            (10, '10'),
            (12, '12'),
            (99, _('Passed')),
             )
    grade = models.CharField(_('grade'), max_length=2, blank=True, choices=GRADES)

    
    def __unicode__(self):
        return self.title or self.slug

    @property
    def friendly_filename(self):
        " A friendly filename (ie not the UUID) for the user to see when they download. "
        return '%s%s' % (self.slug, self.file_extension)

    @property
    def url_pattern_args(self):
        " Arguments for URL patterns using this object. "
        return [self.tribe.slug, self.slug]
    
    class Meta:
        unique_together = ("tribe", "slug")

    def get_absolute_url(self):
        return ("document_view_document_detail", [self.tribe.slug, self.slug])
    get_absolute_url = models.permalink(get_absolute_url)

    class Meta: 
        verbose_name = _(u'Document')
        verbose_name_plural = _(u'Documents')        
# Some automatic metadata handing, if the extractor library is available
try:
    import extractor
    LIB_EXTRACTOR_AVAILABLE = True
except ImportError:
    LIB_EXTRACTOR_AVAILABLE = False

if LIB_EXTRACTOR_AVAILABLE:
    from django_dms import metadata

    class DocumentMetadata(object):
        model = Document
        def process_title(self, value):
            return value.isupper() and value.title() or value
        def process_date_created(self, value):
            # TODO: This should be in the metadata engine
            for pattern in ('%Y-%m-%dT%H:%M:%SZ', '%Y%m%d%H%M%S'):
                try:
                    # String is trimmed to the size of pattern, assuming that
                    # it is the same length as the string it is matching (coincidently, it often is!).
                    return datetime.strptime(value[:len(pattern)], pattern)
                except ValueError:
                    continue
            return value
    
    metadata.register(Document, title='title', file_mimetype='mimetype', date_created='creation date')
