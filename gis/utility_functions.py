from django.db.models.expressions import RawSQL


def points_within_radius(gismodel, latitude, longitude, **kwargs):
    radius = kwargs.get('radius', False)
    use_miles = kwargs.get('use_miles', True)

    if radius:
        radius = float(radius)

    distance_unit = float(3959 if use_miles else 6371)

    # Great circle distance formula
    gcd_formula = "%s * acos(least(greatest(cos(radians(%s)) * cos(radians(latitude)) * cos(radians(longitude) - " \
                  "radians(%s)) + sin(radians(%s)) * sin(radians(latitude)), -1), 1))"
    distance_raw_sql = RawSQL(gcd_formula, (distance_unit, latitude, longitude, latitude))
    qs = gismodel.objects.all().annotate(distance=distance_raw_sql).order_by('distance')

    if radius:
        qs = qs.filter(distance__lt=radius)

    return qs
