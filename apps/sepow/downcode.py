#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# (c) 2008 Harry Kalogirou <harkal@gmail.com>
# 
# * Language maps taken from django's javascript urlify
#

import re

LATIN_MAP = {
    u'À': 'A', u'Á': 'A', u'Â': 'A', u'Ã': 'A', u'Ä': 'A', u'Å': 'Aa', u'Æ': 'AE', u'Ç':'C', 
    u'È': 'E', u'É': 'E', u'Ê': 'E', u'Ë': 'E', u'Ì': 'I', u'Í': 'I', u'Î': 'I',
    u'Ï': 'I', u'Ð': 'D', u'Ñ': 'N', u'Ò': 'O', u'Ó': 'O', u'Ô': 'O', u'Õ': 'O', u'Ö':'O', 
    u'Ő': 'O', u'Ø': 'O', u'Ù': 'U', u'Ú': 'U', u'Û': 'U', u'Ü': 'U', u'Ű': 'U',
    u'Ý': 'Y', u'Þ': 'TH', u'ß': 'ss', u'à':'a', u'á':'a', u'â': 'a', u'ã': 'a', u'ä':'a', 
    u'å': 'aa', u'æ': 'ae', u'ç': 'c', u'è': 'e', u'é': 'e', u'ê': 'e', u'ë': 'e',
    u'ì': 'i', u'í': 'i', u'î': 'i', u'ï': 'i', u'ð': 'd', u'ñ': 'n', u'ò': 'o', u'ó':'o', 
    u'ô': 'o', u'õ': 'o', u'ö': 'o', u'ő': 'o', u'ø': 'o', u'ù': 'u', u'ú': 'u',
    u'û': 'u', u'ü': 'u', u'ű': 'u', u'ý': 'y', u'þ': 'th', u'ÿ': 'y'
}
LATIN_SYMBOLS_MAP = {
    u'©':'(c)'
}
GREEK_MAP = {
    u'α':'a', u'β':'b', u'γ':'g', u'δ':'d', u'ε':'e', u'ζ':'z', u'η':'h', u'θ':'8',
    u'ι':'i', u'κ':'k', u'λ':'l', u'μ':'m', u'ν':'n', u'ξ':'3', u'ο':'o', u'π':'p',
    u'ρ':'r', u'σ':'s', u'τ':'t', u'υ':'y', u'φ':'f', u'χ':'x', u'ψ':'ps', u'ω':'w',
    u'ά':'a', u'έ':'e', u'ί':'i', u'ό':'o', u'ύ':'y', u'ή':'h', u'ώ':'w', u'ς':'s',
    u'ϊ':'i', u'ΰ':'y', u'ϋ':'y', u'ΐ':'i',
    u'Α':'A', u'Β':'B', u'Γ':'G', u'Δ':'D', u'Ε':'E', u'Ζ':'Z', u'Η':'H', u'Θ':'8',
    u'Ι':'I', u'Κ':'K', u'Λ':'L', u'Μ':'M', u'Ν':'N', u'Ξ':'3', u'Ο':'O', u'Π':'P',
    u'Ρ':'R', u'Σ':'S', u'Τ':'T', u'Υ':'Y', u'Φ':'F', u'Χ':'X', u'Ψ':'PS', u'Ω':'W',
    u'Ά':'A', u'Έ':'E', u'Ί':'I', u'Ό':'O', u'Ύ':'Y', u'Ή':'H', u'Ώ':'W', u'Ϊ':'I',
    u'Ϋ':'Y'
}
TURKISH_MAP = {
    u'ş':'s', u'Ş':'S', u'ı':'i', u'İ':'I', u'ç':'c', u'Ç':'C', u'ü':'u', u'Ü':'U',
    u'ö':'o', u'Ö':'O', u'ğ':'g', u'Ğ':'G'
}
RUSSIAN_MAP = {
    u'а':'a', u'б':'b', u'в':'v', u'г':'g', u'д':'d', u'е':'e', u'ё':'yo', u'ж':'zh',
    u'з':'z', u'и':'i', u'й':'j', u'к':'k', u'л':'l', u'м':'m', u'н':'n', u'о':'o',
    u'п':'p', u'р':'r', u'с':'s', u'т':'t', u'у':'u', u'ф':'f', u'х':'h', u'ц':'c',
    u'ч':'ch', u'ш':'sh', u'щ':'sh', u'ъ':'', u'ы':'y', u'ь':'', u'э':'e', u'ю':'yu',
    u'я':'ya',
    u'А':'A', u'Б':'B', u'В':'V', u'Г':'G', u'Д':'D', u'Е':'E', u'Ё':'Yo', u'Ж':'Zh',
    u'З':'Z', u'И':'I', u'Й':'J', u'К':'K', u'Л':'L', u'М':'M', u'Н':'N', u'О':'O',
    u'П':'P', u'Р':'R', u'С':'S', u'Т':'T', u'У':'U', u'Ф':'F', u'Х':'H', u'Ц':'C',
    u'Ч':'Ch', u'Ш':'Sh', u'Щ':'Sh', u'Ъ':'', u'Ы':'Y', u'Ь':'', u'Э':'E', u'Ю':'Yu',
    u'Я':'Ya'
}
UKRAINIAN_MAP = {
    u'Є':'Ye', u'І':'I', u'Ї':'Yi', u'Ґ':'G', u'є':'ye', u'і':'i', u'ї':'yi', u'ґ':'g'
}
CZECH_MAP = {
    u'č':'c', u'ď':'d', u'ě':'e', u'ň':'n', u'ř':'r', u'š':'s', u'ť':'t', u'ů':'u',
    u'ž':'z', u'Č':'C', u'Ď':'D', u'Ě':'E', u'Ň':'N', u'Ř':'R', u'Š':'S', u'Ť':'T',
    u'Ů':'U', u'Ž':'Z'
}

POLISH_MAP = {
    u'ą':'a', u'ć':'c', u'ę':'e', u'ł':'l', u'ń':'n', u'ó':'o', u'ś':'s', u'ź':'z',
    u'ż':'z', u'Ą':'A', u'Ć':'C', u'Ę':'e', u'Ł':'L', u'Ń':'N', u'Ó':'o', u'Ś':'S',
    u'Ź':'Z', u'Ż':'Z'
}

LATVIAN_MAP = {
    u'ā':'a', u'č':'c', u'ē':'e', u'ģ':'g', u'ī':'i', u'ķ':'k', u'ļ':'l', u'ņ':'n',
    u'š':'s', u'ū':'u', u'ž':'z', u'Ā':'A', u'Č':'C', u'Ē':'E', u'Ģ':'G', u'Ī':'i',
    u'Ķ':'k', u'Ļ':'L', u'Ņ':'N', u'Š':'S', u'Ū':'u', u'Ž':'Z'
}

OTHER_MAP = {
    u' ':'-', u"'":'',
}



def _makeRegex():
    ALL_DOWNCODE_MAPS = {}
    ALL_DOWNCODE_MAPS.update(LATIN_MAP)
    ALL_DOWNCODE_MAPS.update(LATIN_SYMBOLS_MAP)
    ALL_DOWNCODE_MAPS.update(GREEK_MAP)
    ALL_DOWNCODE_MAPS.update(TURKISH_MAP)
    ALL_DOWNCODE_MAPS.update(RUSSIAN_MAP)
    ALL_DOWNCODE_MAPS.update(UKRAINIAN_MAP)
    ALL_DOWNCODE_MAPS.update(CZECH_MAP)
    ALL_DOWNCODE_MAPS.update(POLISH_MAP)
    ALL_DOWNCODE_MAPS.update(LATVIAN_MAP)
    ALL_DOWNCODE_MAPS.update(OTHER_MAP)
    
    s = u"".join(ALL_DOWNCODE_MAPS.keys())
    regex = re.compile(u"[%s]|[^%s]+" % (s,s))
    
    return ALL_DOWNCODE_MAPS, regex

_MAPINGS = None
_regex = None

def downcode(s):
    """
    This function is 'downcode' the string pass in the parameter s. This is useful 
    in cases we want the closest representation, of a multilingual string, in simple
    latin chars. The most probable use is before calling slugify.
    """
    global _MAPINGS, _regex
    
    if not _regex:
        _MAPINGS, _regex = _makeRegex()    
        
    downcoded = ""
    for piece in _regex.findall(s):
        if _MAPINGS.has_key(piece):
            downcoded += _MAPINGS[piece]
        else:
            downcoded += piece
    return downcoded


if __name__ == "__main__":
    string = u'Den fælleøs opslagstavle'
    print 'Original  :', string
    print 'Downcoded :', downcode(string)

