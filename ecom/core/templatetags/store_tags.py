from django import template
from django.urls import reverse, NoReverseMatch
from ..models import Estore
from ..forms import SubscribingForm

register = template.Library()

@register.simple_tag(takes_context=True)
def active(context: dict, url_name: str, **kwargs):
    try:
        url = reverse(url_name, kwargs= kwargs)
    except NoReverseMatch:
        return ""
    request = context.get("request")
    if not request:
        return ''
    if request.path == url:
        return 'active'
    return ''

@register.simple_tag(takes_context=True)
def active_name(context: dict):
    request = context.get("request")
    if not request:
        return ''
    parts = (request.path.strip('/')).split('/')
    if parts:
        page_name = parts[-1].replace("_", " ").title()
        return page_name if page_name != '' else "Index"
    else:
        return ''
    

@register.simple_tag
def estore():
    return Estore.objects.filter(current = True).first()

@register.simple_tag
def subscribingForm():
    return SubscribingForm()

@register.filter
def tel_format(value):
    return ''.join(c for c in value if c.isdigit() or c == '+' )