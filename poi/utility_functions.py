import glob
import json
import math
import os
import re
import zipfile

import xmltodict
from django.conf import settings
from filer.management.commands.import_files import FileImporter
from filer.models import Folder, File

from poi.constants import GPX_WAYPOINTS, GPX_GEOCACHES
from poi.models import GPXFile, Point
from gis.utility_functions import points_within_radius


def get_points_in_radius(latitude, longitude, **kwargs):
    caches = points_within_radius(Point, latitude, longitude, **kwargs)

    points = []
    for cache in caches:
        if cache.point_type == GPX_GEOCACHES:
            points.append(cache)

    return points


def process_gpx_file(gpx_file, **kwargs):
    pq = kwargs.get("pocket_query", None)

    media_root_normalized = os.path.join(*os.path.split(settings.MEDIA_ROOT))
    gpxfile = os.path.join(media_root_normalized, str(gpx_file.gpx_file.file))

    with open(gpxfile, "rU", encoding="utf8") as gpx:
        gpx_xml = gpx.read()
        gpx.close()

    gpx_dict = to_dict(xmltodict.parse(gpx_xml)).get("gpx")
    points = gpx_dict.get("wpt")

    for point in points:
        new_point = Point.objects.create(
            name=point.get("name"),
            gpx_type=point.get("type"),
            url=point.get("url"),
            urlname=point.get("urlname"),
            time=point.get("time"),
            sym=point.get("sym"),
            latitude=float(point.get("@lat")),
            longitude=float(point.get("@lon")),
            desc=point.get("desc")
        )

        new_point.gpx_files.add(gpx_file)
        if pq:
            new_point.pocket_query.add(pq)

        if "groundspeak:cache" not in point:
            new_point.point_type = GPX_WAYPOINTS

        else:
            new_point.point_type = GPX_GEOCACHES

            gc_data = point.get("groundspeak:cache")

            new_point.placed_by = gc_data.get("groundspeak:placed_by")
            new_point.long_description = gc_data.get("groundspeak:long_description").get("#text")
            new_point.country = gc_data.get("groundspeak:country")
            new_point.state = gc_data.get("groundspeak:state")
            new_point.difficulty = float(gc_data.get("groundspeak:difficulty"))
            new_point.terrain = gc_data.get("groundspeak:terrain")
            new_point.container = gc_data.get("groundspeak:container")
            new_point.hints = gc_data.get("groundspeak:encoded_hints")

        new_point.save()


def process_pocket_query(obj):
    original_filename = obj.zip_file.original_filename
    filename = obj.zip_file.file
    file_name = str(filename)

    zipfile_path_normalized = os.path.join(*file_name.split("/"))
    media_root_normalized = os.path.join(*os.path.split(settings.MEDIA_ROOT))
    zip_file_path = os.path.join(media_root_normalized, zipfile_path_normalized)

    foldername = original_filename.split(".")[0]
    temp_folder = os.path.join(media_root_normalized, foldername)

    if os.path.exists(zip_file_path):
        df = FileImporter()
        df.get_or_create_folder(["geocaches", foldername])

        try:
            folder = Folder.objects.get(name=foldername)
        except Folder.DoesNotExist:
            pass

        else:
            if not os.path.exists(temp_folder):
                os.mkdir(temp_folder)

            zip_ref = zipfile.ZipFile(zip_file_path, "r")
            zip_ref.extractall(temp_folder)
            zip_ref.close()

            os.remove(zip_file_path)

            df.walker(temp_folder, "geocaches")

            gpx_files = glob.glob(os.path.join(temp_folder, "*.gpx"))

            for gpx_file in gpx_files:
                gpx_filename = os.path.split(gpx_file)[-1]

                file = None

                try:
                    file = File.objects.get(original_filename=gpx_filename)
                except File.MultipleObjectsReturned:
                    files = File.objects.filter(original_filename=gpx_filename)
                    file = files.last()

                except File.DoesNotExist:
                    pass

                if file:
                    os.remove(gpx_file)

                    if "wpts.gpx" in gpx_filename:
                        try:
                            gpxfile = GPXFile.objects.get(gpx_file=file)

                        except GPXFile.DoesNotExist:
                            gpxfile = GPXFile.objects.create(
                                gpx_file=file, file_type=GPX_WAYPOINTS, updated_by=obj.updated_by
                            )

                        obj.waypoints = gpxfile

                    else:
                        try:
                            gpxfile = GPXFile.objects.get(gpx_file=file)

                        except GPXFile.DoesNotExist:
                            gpxfile = GPXFile.objects.create(
                                gpx_file=file, file_type=GPX_GEOCACHES, updated_by=obj.updated_by
                            )

                        obj.geocaches = gpxfile

                    obj.save()

                    if gpxfile:
                        process_gpx_file(gpxfile, pocket_query=obj)

    try:
        os.rmdir(temp_folder)
    except OSError:
        pass


def camel_to_words(value, **kwargs):
    parts_ex = "([A-Z])"
    parts = re.findall(parts_ex, value)

    for part in parts:
        value = value.replace(part, " %s" % part.lower())

    return value


def to_dict(input_ordered_dict):
    return json.loads(json.dumps(input_ordered_dict))
