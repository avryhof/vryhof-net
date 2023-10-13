from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def form_input(field):
    html_parts = []

    html_parts += ['<div class="form-group">']
    html_parts += [f'<label for="{field.id_for_label}">{field.label}</label>', '<div class="input-group">']
    if field.errors:
        html_parts += ['<ul class="error_list">']
        html_parts += [f'<li class="field_error">{error}</li>' for error in field.errors]
        html_parts += ["</ul>"]
    html_parts += [str(field)]
    if field.help_text:
        html_parts += [f'<div class="help-block">{field.help_text}</div>']
    html_parts += ["</div>", "</div>"]

    return mark_safe("".join(html_parts))
