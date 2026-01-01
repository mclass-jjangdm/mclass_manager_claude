from django import template

register = template.Library()

@register.filter
def get_form_field(form, field_name):
    try:
        return form[field_name]
    except KeyError:
        return ''