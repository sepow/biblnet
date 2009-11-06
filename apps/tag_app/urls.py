from django.conf.urls.defaults import *
from sepow.views import *

urlpatterns = patterns('',
    # all tags
    url(r'^a/$', 'tag_app.views.tag_autocomplete', name='tag_autocomplete'),
    url(r'^c/$', 'tag_app.views.combine_tags', name='combine_tags'),
    url(r'^$', 'tag_app.views.show_tag_cloud', name='tag_cloud'),
    url(r'^t/(?P<tag>.+)/$', 'tag_app.views.tags', name='tag_results'),
    
)
