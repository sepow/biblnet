from django import forms
from django.db.models import get_model
from django.utils import simplejson
from django.utils.safestring import mark_safe
from tagging.models import Tag



class AutoCompleteTagInput(forms.Textarea):
    
    def __init__(self, attrs=None, cls=None):
        attrs = {'cols': '20', 'rows': '10'}
        super(AutoCompleteTagInput, self).__init__(attrs)
        self.cls = cls
    
    class Media:
        css = {
            'all': ('js/jquery-autocomplete/jquery.autocomplete.css',)
        }
        js = (
            'js/jquery-autocomplete/lib/jquery.js',
            'js/jquery-autocomplete/lib/jquery.bgiframe.min.js',
            'js/jquery-autocomplete/lib/jquery.ajaxQueue.js',
            'js/jquery-autocomplete/jquery.autocomplete.js'
        )
    def render(self, name, value, attrs=None,):
        output = super(AutoCompleteTagInput, self).render(name, value, attrs)
        page_tags = Tag.objects.usage_for_model(self.cls)
        tag_list = simplejson.dumps([tag.name for tag in page_tags],
                                    ensure_ascii=False)
        return output + mark_safe(u'''<script type="text/javascript">
            jQuery("#id_%s").autocomplete(%s, {
                width: 150,
                max: 10,
                highlight: false,
                multiple: true,
                multipleSeparator: ", ",
                scroll: true,
                scrollHeight: 300,
                matchContains: true,
                autoFill: true,
            });
            </script>''' % (name, tag_list))

