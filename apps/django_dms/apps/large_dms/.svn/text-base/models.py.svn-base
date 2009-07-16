from django.db import models
from django_dms.models import DocumentBase, DocumentInteractionBase
from django.contrib.auth.models import User
from django_dms import friendly_id

class Document(DocumentBase):
    """ Basic document entry for larger document databases.
        Each document has a document_id which is a short string of characters using friendly_id.
        See django_dms/friendly_id.py for important information.
    """
    document_id  = models.CharField("document ID", max_length=10, null=True, blank=True, editable=False, unique=True)
    title        = models.CharField(max_length=150, default="", blank=True)
    summary      = models.TextField(default="", blank=True)
    author       = models.CharField(max_length=150, default="", blank=True)
    date_created = models.DateTimeField("created", null=True, blank=True)

    # Extract plaintext from document and store in database to allow full-text searching
    plaintext    = models.TextField(default="", blank=True, editable=False)
    uploaded_by  = models.ForeignKey(User, null=True, blank=True, editable=False) # NB: Automate this in the form

    def save(self, *args, **kwargs):
        " Save the document object. "
        super(Document, self).save(*args, **kwargs)

        # Populate the document_id if it is missing
        if self.id and not self.document_id:
            self.document_id = friendly_id.encode(self.id)
            super(Document, self).save(*args, **kwargs)

    def __unicode__(self):
        return self.title or self.document_id or u"untitled"

    @property
    def friendly_filename(self):
        " A friendly filename for the user to see when they download. "
        return u'%s.%s' % (self.document_id, self.file_extension)

    @property
    def url_pattern_args(self):
        " Arguments for the url pattern. "
        return [self.document_id]


class DocumentInteraction(DocumentInteractionBase):
    """ Track user interactions with these documents. """
    document    = models.ForeignKey(Document, related_name="interactions")

class TagManager(models.Manager):
    use_for_related_fields = True

    def __call__(self):
        return self.__unicode__()

    def __unicode__(self):
        return ", ".join(t.name for t in self.all().order_by('name'))

class Tag(models.Model):
    """ Allow documents to be categorised. """
    name = models.CharField(max_length=40)
    # Eventualy use generic relation
    documents = models.ManyToManyField(Document, related_name="tags")
    objects = TagManager()

    def __unicode__(self):
        return self.name

    class Meta:
        ordering = ('name',)


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
    
    metadata.register(Document, title='title', file_mimetype='mimetype', author='creator', date_created='creation date')
