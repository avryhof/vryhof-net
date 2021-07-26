import csv

from api.models import PostalCode, GeoName
from gis.utility_functions import points_within_radius
from utilities.aware_datetime import aware_datetime
from utilities.debugging import log_message
from utilities.utility_functions import int_or_none

datetime = aware_datetime()


def postal_codes_within_radius(latitude, longitude, **kwargs):
    return points_within_radius(PostalCode, latitude, longitude, **kwargs)


def import_postal_codes_csv(data_file_path, **kwargs):
    delimiter = kwargs.get("delimiter", "\t")

    data_file = open(data_file_path, "rU", encoding="utf-8")

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
                        admin_name1=row[3],
                        admin_code1=row[4],
                        admin_name2=row[5],
                        admin_code2=row[6],
                        admin_name3=row[7],
                        admin_code3=row[8],
                        latitude=row[9],
                        longitude=row[10],
                        accuracy=row[11],
                        updated=datetime.now(),
                    )
                )

            else:
                postal_code.country_code = row[0]
                postal_code.postal_code = row[1]
                postal_code.name = row[2]
                postal_code.place_name = row[2]
                postal_code.admin_name1 = row[3]
                postal_code.admin_code1 = row[4]
                postal_code.admin_name2 = row[5]
                postal_code.admin_code2 = row[6]
                postal_code.admin_name3 = row[7]
                postal_code.admin_code3 = row[8]
                postal_code.latitude = row[9]
                postal_code.longitude = row[10]
                postal_code.accuracy = row[11]
                postal_code.updated = datetime.now()
                postal_code.save()

    data_file.close()

    PostalCode.objects.bulk_create(insert_list)


def import_geonames_csv(data_file_path, **kwargs):
    delimiter = kwargs.get("delimiter", "\t")
    insert_threshold = kwargs.get("insert_threshold", 10000)

    data_file = open(data_file_path, "rU", encoding="utf8")

    rows = csv.reader(data_file, delimiter=delimiter)

    insert_list = []
    for row in rows:
        if len(row) > 0 and int(row[14]) > 0:
            try:
                place = GeoName.objects.get(geonameid=row[0])

            except GeoName.DoesNotExist:
                insert_list.append(
                    GeoName(
                        geonameid=row[0],
                        name=row[1],
                        asciiname=row[2],
                        alternatenames=row[3],
                        latitude=row[4],
                        longitude=row[5],
                        feature_class=row[6],
                        feature_code=row[7],
                        country_code=row[8],
                        cc2=row[9],
                        admin1_code=row[10],  # 1. order subdivision (state) varchar(20)
                        admin2_code=row[11],  # 2. order subdivision (county/province)
                        admin3_code=row[12],  # 3. order subdivision (community) varchar(20)
                        admin4_code=row[13],  # 3. order subdivision (community) varchar(20)
                        population=row[14],
                        elevation=int_or_none(row[15]),  # in meters
                        dem=row[16],  # digital elevation model, srtm3 or gtopo30
                        timezone=row[17],
                        modification_date=row[18],
                    )
                )

            # else:
            #     place.name = row[1]
            #     place.asciiname = row[2]
            #     place.alternatenames = row[3]
            #     place.latitude = row[4]
            #     place.longitude = row[5]
            #     place.feature_class = row[6]
            #     place.feature_code = row[7]
            #     place.country_code = row[8]
            #     place.cc2 = row[9]
            #     place.admin1_code = row[10]  # 1. order subdivision (state) varchar(20)
            #     place.admin2_code = row[11]  # 2. order subdivision (county/province)
            #     place.admin3_code = row[12]  # 3. order subdivision (community) varchar(20)
            #     place.admin4_code = row[13]  # 3. order subdivision (community) varchar(20)
            #     place.population = row[14]
            #     place.elevation = int_or_none(row[15])  # in meters
            #     place.dem = row[16]  # digital elevation model, srtm3 or gtopo30
            #     place.timezone = row[17]
            #     place.modification_date = row[18]
            #
            #     place.save()

        if len(insert_list) >= insert_threshold:
            GeoName.objects.bulk_create(insert_list)
            log_message(
                "Inserted {} places. Database contains {} places.".format(
                    len(insert_list), GeoName.objects.all().count()
                )
            )
            insert_list = []

    data_file.close()

    GeoName.objects.bulk_create(insert_list)
    log_message(
        "Inserted {} places. Database contains {} places. Final Insert.".format(
            len(insert_list), GeoName.objects.all().count()
        )
    )


def get_place_from_zip(zip_code):
    postal_code = False
    if isinstance(zip_code, str):
        try:
            postal_code = PostalCode.objects.get(postal_code=zip_code)
        except PostalCode.DoesNotExist:
            pass
    elif hasattr(zip_code, "postal_code"):
        postal_code = zip_code

    if postal_code:
        try:
            place = GeoName.objects.get(
                name=postal_code.name,
                country_code=postal_code.country_code,
                admin1_code=postal_code.admin_code1,
                admin2_code=postal_code.admin_code2,
                admin3_code=postal_code.admin_code3,
                feature_class="P",
            )
        except GeoName.DoesNotExist:
            pass
        except GeoName.MultipleObjectsReturned:
            places = GeoName.objects.filter(
                name=postal_code.name,
                country_code=postal_code.country_code,
                admin1_code=postal_code.admin_code1,
                admin2_code=postal_code.admin_code2,
                admin3_code=postal_code.admin_code3,
                feature_class="P",
            )
            print(postal_code.name)
            for place in places:
                print(
                    place.name,
                    place.asciiname,
                    place.country_code,
                    place.admin1_code,
                    place.admin2_code,
                    place.feature_code,
                    place.feature_class,
                    place.population,
                )

        else:
            return place

    return False
