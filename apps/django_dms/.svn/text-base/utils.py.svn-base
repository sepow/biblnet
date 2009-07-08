#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
      Title: DMS framework utilities
    Project: django_dms
     Author: Will Hardy
       Date: November 2008
  $Revision$

"""
import uuid
import hashlib
from datetime import datetime
from django.db import models
from django.utils.encoding import force_unicode, smart_unicode

class ChoicesBank(object):
    """ Allows individual objects to be chosen from choices, without needing the entire queryset.
        This lets the Widget decide which values will be used.
    """
    def __init__(self, queryset):
        self.queryset = queryset

    def only(self, keys):
        return ((key, smart_unicode(val)) for key, val in self.queryset.in_bulk(keys).iteritems())

    def __iter__(self):
        """ Emulate standard choices object. """
        return ((x._get_pk_val(), smart_unicode(x)) for x in self.queryset)

    def __len__(self):
        return len(self.queryset)

from django.utils.translation import ugettext as _

class Choices(tuple):
    """ A more readable, convenient way of declaring translatable choices.  
    """

    def __new__(cls, *args, **kwargs):

        # Create a normalised dictionary of items
        items = {}
        order_list = []

        # Add the keyword arguments as is
        items.update(kwargs)

        # Add the non-keyword arguments, enumerating them automatically
        for value, name in enumerate(args):
            # Avoid clashes in the automatically generated values
            # Explicit values (in the keyword arguments) are allowed to clash
            while value in items.values():
                value += 1
            items[name] = value
            order_list.append(name)

        # keyword arguments come last
        sorted_keywords = [ (value, key) for key, value in kwargs.items() ]
        order_list.extend([ key for value, key in sorted(sorted_keywords) ])

        # Create the actual choices list
        choices = []
        for name in order_list:
            choices.append((items[name], _(name)))

        # Save the choices list as a tuple
        self = super(Choices, cls).__new__(cls, choices)

        # Add our stored value to the object for reference
        for name in order_list:
            # Remove all non-alphanumeric characters, replace with non-repeating underscore
            key = "_".join("".join([ a.isalnum() and a or " " for a in name]).split()).upper()
            setattr(self, key, items[name])

        # Add our dictionary of items for reference
        self._items = items
        self._order_list = order_list
        self._reverse_items = {}
        for key, val in self._items.iteritems():
            self._reverse_items[val] = key

        return self

    # Allow string lookup from keys
    def __getitem__(self, key):
        return self._reverse_items[key]

    def __repr__(self):
        """ Displays a way of re-creating this object. """
        return "Choices(%s)" % ", ".join([ "%s=%s" % (name, self._items[name]) for name in self._order_list ] )



def get_hash(content):
    return hashlib.sha224(content.read()).hexdigest()

class HashField(models.CharField):
    """ Store a hash of the given field.
    """
    def __init__(self, from_field, *args, **kwargs):
        kwargs.setdefault('max_length', 56)
        super(HashField, self).__init__(*args, **kwargs)
        self.from_field = from_field

    def pre_save(self, model_instance, add):
        """ Generate the hash on save. 
        """
        # TODO: When/how often should the hash be generated? every save?
        return get_hash(getattr(model_instance, self.from_field))

    def get_internal_type(self):
        return models.CharField.__name__



# The following field isn't necessary, but is useful for those who just want a UUID field

class UUIDField(models.CharField):
    """ UUIDField
    For convenience and reuse, this is equivalent to:
        models.CharField(max_length=36, default=lambda:unicode(uuid.uuid4()), blank=True, editable=False)

    By using "default", the value is there from the beginning, before the model is saved.
    A better implementation might store the value as an 128 bit integer in the database.
    For more information see: http://docs.python.org/lib/module-uuid.html
    """

    def __init__(self, *args, **kwargs):
        kwargs['max_length'] = 36
        kwargs.setdefault('default', lambda: unicode(uuid.uuid4()))
        kwargs.setdefault('blank', True)
        kwargs.setdefault('editable', False)
        super(UUIDField, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        return models.CharField.__name__
