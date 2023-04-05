from django import template
from mailing.forms import MailingForm


register = template.Library()


@register.inclusion_tag('mailing/tags/mailing_form.html')
def mailing_form():
    return {'mailing_form': MailingForm()}
