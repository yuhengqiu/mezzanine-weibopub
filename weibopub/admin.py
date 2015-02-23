from __future__ import unicode_literals

from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _
from django.template.defaultfilters import truncatechars

from mezzanine.weibopub import get_auth_settings

FORMFIELD_HTML = """
<div class='send_weibo_container'>
    <input id='id_send_weibo' name='send_weibo' type='checkbox'>
    <label class='vCheckboxLabel' for='id_send_weibo'>%s</label>
</div>
"""

class WeiboAdminMixin(object):
    """
    Admin mixin that adds a "Send to Weibo" checkbox to the add/change
    views, which when checked, will send a weibo with the title、pic and link
    to the object being saved.
    """

    def formfield_for_dbfield(self, db_field, **kwargs):
        """
        Adds the "Send to Weibo" checkbox after the "status" field,
        provided by any ``Displayable`` models. The approach here is
        quite a hack, however the sane approach of using a custom
        form with a boolean field defined, and then adding it to the
        formssets attribute of the admin class fell apart quite
        horrifically.
        """
        formfield = super(WeiboAdminMixin,
            self).formfield_for_dbfield(db_field, **kwargs)
        if db_field.name == "status" and get_auth_settings():
            def wrapper(render):
                def wrapped(*args, **kwargs):
                    rendered = render(*args, **kwargs)
                    label = _("Pub to Weibo")
                    return mark_safe(rendered + FORMFIELD_HTML % label)
                return wrapped
            formfield.widget.render = wrapper(formfield.widget.render)
        return formfield

    def save_model(self, request, obj, form, change):
        """
        Sends a weibo with the title/pic/short_url if applicable.
        """
        super(WeiboAdminMixin, self).save_model(request, obj, form, change)
        if request.POST.get("send_weibo", False):
            auth_settings = get_auth_settings()
            obj.set_short_url()
            message = truncatechars(obj, 140 - len(obj.short_url) - 1)
            api = Api(*auth_settings)
            api.update.post(u'%s。[阅读全文:%s]'%(message,obj.short_url),pic=open('/Users/test.png'))
