# -*- coding: utf-8 -*-

import re
from django import template
from django.conf import settings
from django.utils.encoding import force_unicode
from django.utils.safestring import mark_safe
from sepow.downcode import downcode
try:
    WIKI_WORD_RE = settings.WIKI_WORD_RE
except AttributeError:
    #WIKI_WORD_RE = r"\[\[([\wøæå ]+)\]\]"
    WIKI_WORD_RE = r"\[\[([\wæøå \-]+)(?:\|([\wæøå \-]+)\]\]|\]\])"
try:
    WIKI_URL_RE = settings.WIKI_URL_RE
except AttributeError:
    WIKI_URL_RE = u'[\w_\-]+' 


wikiwordfier = re.compile(WIKI_WORD_RE, re.U)
#wikiwordfier = re.compile(r'\b(%s)\b' % WIKI_WORD)

register = template.Library()

@register.filter
def wikiwords(s):
    """ Transform every WikiWord in a text into links.
        WikiWord must match this regular expression:
        '(?:[A-Z]+[a-z]+){2,}'
    """
    # @@@ TODO: absolute links
    
    def slugify_wikiword(match):
        wiki_url = '<a href="../%s/">%s</a>' % (downcode(match.group(2) or match.group(1)).lower(), match.group(1))
        return wiki_url
    s = re.sub(wikiwordfier, slugify_wikiword, s)
    
    #s = wikiwordfier.sub(r'<a href="../\1/">\1</a>', s)
    return force_unicode(s)
wikiwords.is_safe = True


@register.inclusion_tag('wiki/article_content.html')
def render_content(article, content_attr='content', markup_attr='markup'):
    """ Display an the body of an article, rendered with the right markup.

    - content_attr is the article attribute that will be rendered.
    - markup_attr is the article atribure with the markup that used
      on the article. the choices are:
      - 'rst' for reStructuredText
      - 'mrk' for Markdown
      - 'txl' for Textile

    Use examples on templates:

        {# article have a content and markup attributes #}
        {% render_content article %}

        {# article have a body and markup atributes #}
        {% render_content article 'body' %}

        {# we want to display the  summary instead #}
        {% render_content article 'summary' %}

        {# post have a tease and a markup_style attributes #}
        {% render_content post 'tease' 'markup_style' %}

        {# essay have a content and markup_lang attributes #}
        {% render_content essay 'content' 'markup_lang' %}

    """
    return {
        'content': getattr(article, content_attr),
        'markup': getattr(article, markup_attr)
    }


@register.inclusion_tag('wiki/article_teaser.html')
def show_teaser(article):
    """ Show a teaser box for the summary of the article.
    """
    return {'article': article}


@register.inclusion_tag('wiki/wiki_title.html')
def wiki_title(group):
    """ Display a <h1> title for the wiki, with a link to the group main page.
    """
    return {'group_name': group.name,
            'group_url': group.get_absolute_url()}
