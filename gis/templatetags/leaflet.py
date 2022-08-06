from django import template
from django.conf import settings
from django.utils.safestring import mark_safe
from frontend_assets.templatetags.utils import render_javascript_code

from utilities.url_helpers import url_join

register = template.Library()

static_root = settings.STATIC_URL


@register.simple_tag
def leaflet_css():
    return mark_safe('<link rel="stylesheet" href="{}"/>'.format(url_join(static_root, "leaflet/leaflet.css")))


@register.simple_tag
def leaflet_javascript():
    return mark_safe('<script src="{}"></script>'.format(url_join(static_root, "leaflet/leaflet.js")))


@register.simple_tag
def leaflet_map(latitude=None, longitude=None, zoom=16, map_prefix="leaflet", map_tiles=False, map_attr=False):
    if not map_tiles:
        map_tiles = "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        map_attr = (
            'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, '
            '<a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>, '
        )
    map_id = "%s_map" % map_prefix
    div = '<div id="%s"></div>' % map_id
    coords = "var %s_coords = [%s, %s];" % (map_prefix, latitude, longitude)
    map = "var %s = L.map('%s').setView(%s_coords, %s);" % (map_id, map_id, map_prefix, zoom)
    tile_layer = "L.tileLayer('%s', {maxZoom: 18, attribution: '%s', id: '%s_streets'}).addTo(%s);" % (
        map_tiles,
        map_attr,
        map_prefix,
        map_id,
    )

    return mark_safe(div) + render_javascript_code([coords, map, tile_layer])


@register.simple_tag
def leaflet_marker(map_prefix="leaflet", latitude=None, longitude=None):
    map_id = "%s_map" % map_prefix
    coords = "var %s_marker_coords = [%s, %s];" % (map_prefix, latitude, longitude)
    code = "L.marker(%s_marker_coords).addTo(%s);" % (map_prefix, map_id)

    return render_javascript_code([coords, code])


@register.simple_tag
def leaflet_tiles(provider="openstreetmap", lang="EN"):
    lang = lang.upper()

    providers = {
        "openstreetmap": {
            "EN": {
                "tiles": "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
                "attr": 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors, '
                '<a href="https://creativecommons.org/licenses/by-sa/2.0/">CC-BY-SA</a>',
            },
        },
        "mapnik": {
            "EN": {
                "tiles": "https://tiles.wmflabs.org/bw-mapnik/{z}/{x}/{y}.png",
                "attr": 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors',
            },
            "DE": {
                "tiles": "https://{s}.tile.openstreetmap.de/tiles/osmde/{z}/{x}/{y}.png",
                "attr": 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors',
            },
            "CH": {
                "tiles": "https://tile.osm.ch/switzerland/{z}/{x}/{y}.png",
                "attr": 'Map data &copy; <a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors',
            },
            "FR": {
                "tiles": "https://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png",
                "attr": "&copy; Openstreetmap France | Map data &copy; "
                '<a href="https://www.openstreetmap.org/">OpenStreetMap</a> contributors',
            },
            "HOT": {
                "tiles": "https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png",
                "attr": "{attribution.OpenStreetMap},  Tiles style by "
                '<a href="https://www.hotosm.org/" target="_blank">Humanitarian OpenStreetMap Team</a> '
                'hosted by <a href="https://openstreetmap.fr/" target="_blank">OpenStreetMap France</a>',
            },
        },
        "openseamap": {
            "EN": {
                "tiles": "https://tiles.openseamap.org/seamark/{z}/{x}/{y}.png",
                "attr": 'Map data: &copy; <a href="http://www.openseamap.org">OpenSeaMap</a> contributors',
            }
        },
        "opentopomap": {
            "EN": {
                "tiles": "https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
                "attr": "Map data: {attribution.OpenStreetMap}, "
                '<a href="http://viewfinderpanoramas.org">SRTM</a> | Map style: &copy; '
                '<a href="https://opentopomap.org">OpenTopoMap</a> '
                '(<a href="https://creativecommons.org/licenses/by-sa/3.0/">CC-BY-SA</a>)',
            }
        },
        "wikimedia": {
            "EN": {
                "tiles": "https://maps.wikimedia.org/osm-intl/{z}/{x}/{y}{r}.png",
                "attr": '<a href="https://wikimediafoundation.org/wiki/Maps_Terms_of_Use">Wikimedia</a>',
            }
        },
    }

    return mark_safe(
        "<script>\nosm_tiles = '{}';\nosm_attr = '{}';\n</script>".format(
            providers.get(provider).get(lang).get("tiles"),
            providers.get(provider).get(lang).get("attr"),
        )
    )
