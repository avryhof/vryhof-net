import requests


class Wikipedia(object):
    session = requests.Session()
    api_url = "https://en.wikipedia.org/w/api.php"

    def get_by_coordinates(self, latitude, longitude):
        """
        "https://en.wikipedia.org/w/api.php
        ?
        action=query
        &
        format=json
        &
        list=geosearch
        &
        gscoord={}%7C{}
        &
        gsradius=10000
        &
        gslimit=100".format(postal_code.latitude, postal_code.longitude)

        :param latitude:
        :param longitude:
        :return:
        """

        params = dict(
            action="query",
            # format="json",
            list="geosearch",
            # prop="coordinates",
            gscoord="{}|{}".format(round(latitude, 7), round(longitude, 7)),
            gsradius=1000,
            gslimit=3,
        )
        resp = self.session.get(url=self.api_url, params=params)

        return resp.json()
