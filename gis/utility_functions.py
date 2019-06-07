def points_within_radius(gismodel, latitude, longitude, **kwargs):
    radius = kwargs.get('radius', False)

    if radius:
        radius = float(radius)

    if kwargs.get('use_miles', True):
        distance_unit = 3959
    else:
        distance_unit = 6371

    table_name = gismodel._meta.db_table

    distance_unit = float(distance_unit)

    sql = 'SELECT id, latitude, longitude, ' \
          '(%f * acos(cos(radians(%s)) * cos(radians(latitude)) * cos(radians(longitude) - ' \
          'radians(%s)) + sin(radians(%s)) * sin(radians(latitude)))) AS distance ' \
          'FROM %s ORDER BY distance;' % (
              distance_unit,
              str(latitude),
              str(longitude),
              str(latitude),
              table_name
          )

    points = []
    for point in gismodel.objects.raw(sql):
        if radius and point.distance > radius:
            break
        else:
            point_object = gismodel.objects.get(id=point.id)
            point_object.distance = point.distance
            points.append(point_object)

    return points
