#!/usr/bin/env python
# -*- coding: UTF-8 -*-
""" Generates and decodes an unique ID, which can use characters
    to shorten its length.

     Author: Will Hardy
       Date: December 2008
      Usage: >>> encode(1)
             "488KR"
  $Revision$
Description: Invoice numbers like "0000004" are unprofessional in that they 
             expose how many sales a system has made, and can be used to monitor
             the rate of sales over a given time.  They are also harder for 
             customers to read back to you, especially if they are 10 digits 
             long.  
             These functions convert an integer (from eg an ID AutoField) to a
             short unique string. This is done simply using a perfect hash
             function and converting the result into a string of user friendly
             characters.

"""
import math
import warnings

try:
    from django.conf import settings
    # Prod the lazy settings to provoke any ImportError caused by a 
    # missing settings file
    getattr(settings, 'DEBUG', None)
except ImportError:
    settings = None

# Keep this small for shorter strings, but big enough to avoid changing
# it later. If you do change it later, it might be a good idea to specify a
# STRING_LENGTH change, making all future strings longer, and therefore unique.
SIZE = getattr(settings, 'FRIENDLY_ID_SIZE', 10000000)

# OPTIONAL PARAMETERS
# This just means we don't start with the first number, to mix things up
OFFSET = getattr(settings, 'FRIENDLY_ID_OFFSET', SIZE / 2 - 1)
# Alpha numeric characters, only uppercase, no confusing values (eg 1/I,0/O,Z/2)
# Remove some letters if you prefer more numbers in your strings
# You may wish to remove letters that sound similar, to avoid confusion when a
# customer calls on the phone (B/P, M/N, 3/C/D/E/G/T/V)
VALID_CHARS = getattr(settings, 'FRIENDLY_ID_VALID_CHARS', 
                                        "3456789ACDEFGHJKLQRSTUVWXY")
# Don't set this if you don't know what you're doing, you run the risk
# It can be used to mix up the strings differently to how others using this code
# would, but be careful to pick a factor of SIZE.
PERIOD = getattr(settings, 'FRIENDLY_ID_PERIOD', None)
# Don't set this, it isn't necessary and you'll get ugly strings like 'AAAAAB3D'
# It will be otherwise done automatically to match SIZE
STRING_LENGTH = getattr(settings, 'FRIENDLY_ID_STRING_LENGTH', None)


def find_suitable_period():
    """ Automatically find a suitable period to use.
        Factors are best, because they will have 1 left over when 
        dividing SIZE+1.
        This only needs to be run once, on import.
    """
    # The highest acceptable factor will be the square root of the size.
    highest_acceptable_factor = int(math.sqrt(SIZE))

    # Too high a factor (eg SIZE/2) and the interval is too small, too 
    # low (eg 2) and the period is too small.
    # We would prefer it to be lower than the number of VALID_CHARS, but more
    # than say 4.
    starting_point = len(VALID_CHARS) > 14 and len(VALID_CHARS)/2 or 13
    for p in range(starting_point, 7, -1) \
                + range(highest_acceptable_factor, starting_point+1, -1) \
                + [6,5,4,3,2]:
        if SIZE % p == 0:
            return p
    raise Exception, "No valid period could be found for SIZE=%d.\n" \
                     "Try avoiding prime numbers :-)" % SIZE

# Set the period if it is missing
if not PERIOD:
    PERIOD = find_suitable_period()


def perfect_hash(num):
    """ Translate a number to another unique number, using a perfect hash function.
        Only meaningful where 0 <= num <= SIZE.
    """
    return ((num+OFFSET)*(SIZE/PERIOD)) % (SIZE+1) + 1


def friendly_number(num):
    """ Convert a base 10 number to a base X string.
        Charcters from VALID_CHARS are chosen, to convert the number 
        to eg base 24, if there are 24 characters to choose from.
        Use valid chars to choose characters that are friendly, avoiding
        ones that could be confused in print or over the phone.
    """
    # Convert to a (shorter) string for human consumption
    string = ""
    # The length of the string can be determined by STRING_LENGTH or by how many
    # characters are necessary to present a base 30 representation of SIZE.
    while STRING_LENGTH and len(string) <= STRING_LENGTH \
                or len(VALID_CHARS)**len(string) <= SIZE:
        # PREpend string (to remove all obvious signs of order)
        string = VALID_CHARS[num%len(VALID_CHARS)] + string
        num = num/len(VALID_CHARS)
    return string


def encode(num):
    """ Encode a simple number, using a perfect hash and converting to a 
        more user friendly string of characters.
    """
    # Check the number is within our working range
    if num > SIZE: return None
    if num < 0: return None

    return friendly_number(perfect_hash(num))


def quick_test():
    """ Check that the period is simply a factor of size, 
        meaning that there will be a single remainder.
        Other period values may be possible (non-cyclic),
        this test will not be able to detect those.
    """
    if PERIOD < 2:
        return False
    if SIZE % PERIOD != 0:
        return False
    return True

# Quickly check that SIZE and PERIOD are usable
# Warn if there might be a problem (quick_test is not fullproof)
if not quick_test():
    warnings.warn("Possibly bad combination of SIZE and PERIOD, string uniqueness has been threatened.")


def test():
    """ Test every single value for uniqueness and that they are properly decoded.
        This can take some time for large SIZE values, but need only be done once
        if the settings do not change.
    """
    # Check all numbers are unique
    from collections import defaultdict
    a = defaultdict()
    for i in range(SIZE+1):
        if encode(i) in a:
            return False
        a[encode(i)] = i

def performance_test():
    """ Run test for the given data to test system performance. 
        (This is used for developing optimisations)
    """
    from timeit import Timer
    t = Timer("test()", "from __main__ import test")
    print t.timeit(number=1)


if __name__ == '__main__':
    # assert test()
    performance_test()

