from geo_ez.us_census_class import USCensus


def geocode(location):
    usc = USCensus()

    valid_address = dict(
        address1=location.address1,
        address2=location.address2,
        city=location.city,
        state=location.state,
        zip_code=location.zip_code,
    )

    geocoded = usc.geocode(query=valid_address)
    if geocoded:
        location.latitude = geocoded.get("latitude")
        location.longitude = geocoded.get("longitude")
        location.save()


def generate_abbreviation(name):
    pieces = name.split()
    abbreviation = name[0:2] if len(pieces) == 1 else "".join([x[0] for x in pieces])

    return abbreviation
