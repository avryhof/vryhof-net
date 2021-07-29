import csv
import datetime
import math
import os
import zipfile
from urllib.request import urlretrieve

import bleach
from django.conf import settings
from django.db.models.expressions import RawSQL
from django.utils.timezone import make_aware

from gis.models import PostalCode
from gis.us_census_class import USCensus
from gis.usps_class import USPS
from utilities.debugging import log_message
from utilities.utility_functions import string_or_none, int_or_none


def geocode(address_dict, **kwargs):
    address_normalized = kwargs.get("normalized", False)

    search_address = dict(
        address1=address_dict.get("address1"),
        address2=address_dict.get("address2"),
        city=address_dict.get("city"),
        state=address_dict.get("state"),
        zip_code=address_dict.get("zip_code"),
    )

    if not address_normalized:
        # First, we normalize the address with the US Postal Service
        ps = USPS()
        valid_address = ps.address(**search_address)
    else:
        valid_address = search_address

    usc = USCensus()

    return usc.geocode(query=valid_address)


def miles_to_km(miles):
    return miles * 1.60934


def km_to_miles(km):
    return km * 0.621371


def deg2rad(deg):
    return deg * (math.pi / 180)


def get_distance(lat1, lon1, lat2, lon2, **kwargs):
    use_miles = kwargs.get("use_miles", True)

    lat1 = float(lat1)
    lat2 = float(lat2)
    lon1 = float(lon1)
    lon2 = float(lon2)

    radius = 6371  # Radius of the earth in km

    d_lat = deg2rad(lat2 - lat1)  # deg2rad below
    d_lon = deg2rad(lon2 - lon1)

    a = math.sin(d_lat / 2) * math.sin(d_lat / 2) + math.cos(deg2rad(lat1)) * math.cos(deg2rad(lat2)) * math.sin(
        d_lon / 2
    ) * math.sin(d_lon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = radius * c  # Distance in km

    if not use_miles:
        return_value = distance
    else:
        return_value = km_to_miles(distance)

    return return_value


def file_is_expired(file_path, days=30):
    if not os.path.exists(file_path):
        is_expired = True
    else:
        today = datetime.datetime.today()
        modified_date = datetime.datetime.fromtimestamp(os.path.getmtime(file_path))
        file_age = today - modified_date
        is_expired = file_age.days > days
    return is_expired


def download_new_file(file_link, target_file):
    if os.path.exists(target_file):
        log_message("Removing file: {}".format(target_file))
        os.remove(target_file)

    log_message("Downloading new file.")
    urlretrieve(file_link, target_file)

    return target_file


def get_geoname_data():
    media_root_normalized = os.path.join(*os.path.split(settings.MEDIA_ROOT))
    zip_file_path = os.path.join(media_root_normalized, "geonames")

    zip_file = os.path.join(zip_file_path, "ALL.zip")

    if file_is_expired(zip_file, 30):
        if not os.path.exists(zip_file_path):
            os.makedirs(zip_file_path)

        if os.path.exists(zip_file):
            os.remove(zip_file)

        urlretrieve("https://github.com/avryhof/postal_codes/archive/master.zip", zip_file)

        zip_ref = zipfile.ZipFile(zip_file, "r")
        zip_ref.extractall(zip_file_path)

        zip_ref.close()

    return os.path.join(zip_file_path, "postal_codes-master")


def get_postal_code_by_coords(latitude, longitude):
    """
    Finds the nearest postal code to the provided coordinates.

    :param latitude:
    :param longitude:
    :return:
    """
    retn = None
    result_count = 0
    radius = 1
    while result_count == 0:
        postal_codes = postal_codes_within_radius(latitude, longitude, radius=radius)
        result_count = len(postal_codes)
        if result_count > 0:
            retn = postal_codes[0]
            break
        radius = radius + 1

    return retn


def points_within_radius(gismodel, latitude, longitude, **kwargs):
    radius = kwargs.get("radius", False)
    use_miles = kwargs.get("use_miles", True)

    if radius:
        radius = float(radius)

    distance_unit = float(3959 if use_miles else 6371)

    # Great circle distance formula
    gcd_formula = (
        "%s * acos(least(greatest(cos(radians(%s)) * cos(radians(latitude)) * cos(radians(longitude) - "
        "radians(%s)) + sin(radians(%s)) * sin(radians(latitude)), -1), 1))"
    )
    distance_raw_sql = RawSQL(gcd_formula, (distance_unit, latitude, longitude, latitude))
    qs = gismodel.objects.all().annotate(distance=distance_raw_sql).order_by("distance")

    if radius:
        qs = qs.filter(distance__lt=radius)

    return qs


def postal_codes_within_radius(latitude, longitude, **kwargs):
    return points_within_radius(PostalCode, latitude, longitude, **kwargs)


def import_postal_codes_csv(data_file_path, **kwargs):
    delimiter = kwargs.get("delimiter", "\t")

    data_file = open(data_file_path, "rU", encoding="utf8")

    rows = csv.reader(data_file, delimiter=delimiter)

    insert_list = []
    for row in rows:
        if len(row) > 0 and row[11]:
            try:
                postal_code = PostalCode.objects.get(postal_code=row[1], name=row[2], place_name=row[2])

            except PostalCode.DoesNotExist:
                insert_list.append(
                    PostalCode(
                        country_code=row[0],
                        postal_code=row[1],
                        name=row[2],
                        place_name=row[2],
                        admin_name1=string_or_none(row[3]),
                        admin_code1=string_or_none(row[4]),
                        admin_name2=string_or_none(row[5]),
                        admin_code2=string_or_none(row[6]),
                        admin_name3=string_or_none(row[7]),
                        admin_code3=string_or_none(row[8]),
                        latitude=float(row[9]),
                        longitude=float(row[10]),
                        accuracy=int_or_none(row[11]),
                        updated=make_aware(datetime.datetime.now()),
                    )
                )

            else:
                postal_code.country_code = row[0]
                postal_code.postal_code = row[1]
                postal_code.name = row[2]
                postal_code.place_name = row[2]
                postal_code.admin_name1 = string_or_none(row[3])
                postal_code.admin_code1 = string_or_none(row[4])
                postal_code.admin_name2 = string_or_none(row[5])
                postal_code.admin_code2 = string_or_none(row[6])
                postal_code.admin_name3 = string_or_none(row[7])
                postal_code.admin_code3 = string_or_none(row[8])
                postal_code.latitude = float(row[9])
                postal_code.longitude = float(row[10])
                postal_code.accuracy = int_or_none(row[11])
                postal_code.updated = make_aware(datetime.datetime.now())
                postal_code.save()

    data_file.close()

    PostalCode.objects.bulk_create(insert_list)


def zip_codes_in_radius(**kwargs):
    zip_code = kwargs.get("zip_code", None)
    radius = kwargs.get("radius", False)
    distance_units = bleach.clean(kwargs.get("distance_units", "miles"))

    if distance_units.lower() in ["mi", "miles", "imperial", "empirical", "us", "united states", "usa"]:
        use_miles = True

    starting_zip_code = PostalCode.objects.get(postal_code=zip_code)

    zipcodes_in_radius = points_within_radius(
        PostalCode, starting_zip_code.latitude, starting_zip_code.longitude, radius=radius, use_miles=True
    )

    zip_codes = []
    for zip_code in zipcodes_in_radius:
        zip_codes.append(
            {
                "zip_code": zip_code.postal_code,
                "distance": round(zip_code.distance, 3),
                "city": zip_code.place_name,
                "state": zip_code.admin_code1,
            }
        )

    return zip_codes
