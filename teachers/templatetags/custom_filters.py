from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def sum_column(salary_table, month):
    return sum(row.get(month, 0) for row in salary_table)


@register.filter(name='phone_number')
def phone_number(number):
    if not number:
        return ''
    number = ''.join(filter(str.isdigit, number))
    if len(number) == 11:
        return f"{number[:3]}-{number[3:7]}-{number[7:]}"
    elif len(number) == 10:
        return f"{number[:3]}-{number[3:6]}-{number[6:]}"
    else:
        return number