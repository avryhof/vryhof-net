from django import template
from django.conf import settings
from frontend_assets.templatetags.utils import render_javascript_code

register = template.Library()

static_root = settings.STATIC_URL

@register.simple_tag
def waypoint_marker(map_prefix='leaflet', latitude=None, longitude=None, waypoint_name=None):
    map_id = '%s_map' % map_prefix
    coords = 'var %s_marker_coords = [%s, %s];' % (waypoint_name, latitude, longitude)
    code = 'L.marker(%s_marker_coords).addTo(%s);' % (waypoint_name, map_id)

    return render_javascript_code([coords, code])