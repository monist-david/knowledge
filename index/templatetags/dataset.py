from django.template.defaultfilters import register
from django import template

from index import models

register = template.Library()

@register.filter
def isint(number):
    return type(number) == int