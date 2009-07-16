#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""
      Title: Metadata extractor
    Project: django_dms
     Author: Will Hardy
       Date: November 2008
  $Revision$

"""

import datetime

from django.db.models.signals import pre_save 
from django.db import models


def extract_metadata(sender, instance, field_mapping, force=False):
    """ Extract and populate metadata from the file itself.
        @force: Overwrite existing metadata
    """
    import extractor as libextractor
    extractor = libextractor.Extractor(lang="en")

    if not extractor:
        return

    all_keywords = extractor.extract(data=instance.file.read(), size=instance.file.size)
    keywords = dict(all_keywords)

    for attr, field in field_mapping.items():
        if field in keywords and (force or not hasattr(instance, attr)):
            # 1. Extract data
            value = keywords[field].encode('iso-8859-1')

            # 2. Post-extraction processing
            try:
                value = getattr(instance, 'process_metadata_%s' % attr)(value)

            # No value processing defined, maybe try some basic automatic processing
            except AttributeError:
                # Date/time processing
                if isinstance(instance._meta.get_field(field), (models.DateField, models.DateTimeField)):
                    for pattern in ('%Y-%m-%dT%H:%M:%SZ', '%Y%m%d%H%M%S'):
                        try:
                            # String is trimmed to the size of pattern, assuming that
                            # it is the same length as the string it is matching (coincidently, it often is!).
                            value = datetime.strptime(value[:len(pattern)], pattern)
                        except ValueError:
                            continue

            # 3. Set the discovered value
            if value:
                setattr(instance, attr, value)


    # TODO: Other keywords might have multiple values, it would be better to handle that properly
    if hasattr(instance, 'plaintext'):
        for key, value in all_keywords:
            if key == 'unknown':
                instance.plaintext += ' ' + value

def register(model, *fields, **kwfields):
    """ Register a given model. """

    field_mapping = kwfields.update(zip(fields, fields))

    def extract_metadata_socket(sender, instance, **kwargs):
        extract_metadata(sender, instance, field_mapping)

    # TODO: Allow extraction fields to be determined
    pre_save.connect(extract_metadata_socket, sender=model)
