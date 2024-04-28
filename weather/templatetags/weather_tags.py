from django import template

register = template.Library()

@register.filter
def intval(value):
    return int(value)

@register.filter
def round_number(value, digits=1):
    return round(value, digits)

@register.simple_tag
def calc_direction(degrees):
    if degrees > 22.5 and degrees < 67.5:
        return "NE"
    elif degrees > 67.5 and degrees < 112.5:
        return "E"
    elif degrees > 112.5 and degrees < 157.5:
        return "SE"
    elif degrees > 157.5 and degrees < 202.5:
        return "S"
    elif degrees > 202.5 and degrees < 247.5:
        return "SW"
    elif degrees > 247.5 and degrees < 292.5:
        return "W"
    elif degrees > 292.5 and degrees < 337.5:
        return "NW"
    else:
        return "N"

