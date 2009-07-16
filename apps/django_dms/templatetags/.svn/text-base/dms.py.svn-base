#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
      Title: 
    Project: 
     Author: Will Hardy
       Date:  2008
      Usage: 
  $Revision$

Description: 

"""

from django import template
from django.core.urlresolvers import reverse

register = template.Library()

def do_dms_url(parser, token):
    """ This is a very simple variant of {% url %}, with none of its extra features. """
    tokens = token.split_contents()
    tag_name, dms_site, url_name = tokens[:3]
    args = tokens[3:]
    return DMSReverse(dms_site, url_name, args)

class DMSReverse(template.Node):
    def __init__(self, dms_site, url_name, args):
        self.dms_site = template.Variable(dms_site)
        self.url_name = url_name
        self.args = [ template.Variable(arg) for arg in args ]
    def render(self, context):
        site = self.dms_site.resolve(context)
        try:
            args = self.args[0].resolve(context).url_pattern_args
        except AttributeError:
            args = [ arg.resolve(context) for arg in self.args ]
        if not site:
            raise template.TemplateSyntaxError, "site missing from dms_url"
        return reverse('%s_%s' % (site.name, self.url_name), args=args)

#@register.simple_tag
#def dms_url(dms_site, url_name):
    #return reverse('%s_%s' % (dms_site, url_name))
register.tag('dms_url', do_dms_url)


