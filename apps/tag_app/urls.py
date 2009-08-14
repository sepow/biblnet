from django.conf.urls.defaults import *
from sepow.views import *

urlpatterns = patterns('',
    # all tags
    url(r'^$', 'sepow.views.show_tag_cloud', name='tag_cloud'),
    url(r'^(?P<tag>.+)/$', 'tag_app.views.tags', name='tag_results'),
)
