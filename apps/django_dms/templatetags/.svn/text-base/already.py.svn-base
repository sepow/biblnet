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

register = template.Library()

@register.filter
def already_viewed(document, request):
    try:
        return document.already("viewed", request)
    except:
        return ''

@register.filter
def already_sent(document, request):
    try:
        return document.already("sent", request)
    except:
        return ''

@register.filter
def already_downloaded(document, request):
    try:
        return document.already("downloaded", request)
    except:
        return ''
