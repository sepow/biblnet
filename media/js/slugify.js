// Based Upon DjangoSnippets: http://www.djangosnippets.org/snippets/1488/
jQuery.fn.slugify = function(obj) {
    jQuery(this).data('origquery', this);
    jQuery(this).data('obj', jQuery(obj));
    jQuery(this).keyup(function() {
        var obj = jQuery(this).data('obj');
        var oquery = jQuery(this).data('origquery');
        var vals = [];
        jQuery(oquery).each(function (i) {
            vals[i] = (jQuery(this).val());
        });
        var slug = vals.join(' ').toLowerCase().replace(/\s+/g,'-').replace(/æ/g,'a').replace(/ø/g,'o').replace(/å/g,'a').replace(/[^a-z0-9-]/g,'');
        obj.val(slug);
    });
}

