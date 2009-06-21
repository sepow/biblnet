from django import template

register = template.Library()

def insert_markitup(obj):
    return {
        'object': obj, 
    }
    
register.inclusion_tag('sepow/markitup.html')(insert_markitup)


from BeautifulSoup import BeautifulSoup, Comment
import re

RE_EXXX = re.compile('j[\s]*(&#x.{1,7})?a[\s]*(&#x.{1,7})?v[\s]*(&#x.{1,7})?a[\s]*(&#x.{1,7})?s[\s]*(&#x.{1,7})?c[\s]*(&#x.{1,7})?r[\s]*(&#x.{1,7})?i[\s]*(&#x.{1,7})?p[\s]*(&#x.{1,7})?t', re.IGNORECASE)

def sanitize_html(value): #TODO execute at topic.save. 
    valid_tags = [
                    'br', 'strong', 'b', 'p', 'div', 'em', 'u', 'strike', 'ul',
                    'li', 'ol', 'a', 'img', 'highlight', 'sup', 'sub', 'span',
                    'big', 'small', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7',
                    'h8', 'pre', 'address', 'code', 'kbd', 'samp', 'var',
                    'del', 'ins', 'cite', 'q', 'bdo','embed', 'object'
                 ] # embed og object er unsafe...

    valid_attrs = 'href src width name height'.split() # kun src og href hvis de starter med http://
    soup = BeautifulSoup(value)
    for comment in soup.findAll(
        text=lambda text: isinstance(text, Comment)):
        comment.extract()
    for tag in soup.findAll(True):
        
        if tag.name not in valid_tags:

            tag.hidden = True

        def passes(attr, val): # It's important that these two attrs start with either www or http imo.
            if not attr == "src" and not attr == "href":
                return True
            else: 
                if str(val).startswith("http") or str(val).startswith("www"):
                    return True
            return False
            
        tag.attrs = [(attr, val) for attr, val in tag.attrs
                     if attr in valid_attrs and passes(attr, val)]
                   
    return re.sub(RE_EXXX, '', soup.renderContents().decode('utf8'))
sanitize_html.is_safe = True
register.filter('sanitize', sanitize_html)

