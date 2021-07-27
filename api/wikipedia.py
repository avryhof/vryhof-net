import requests


class Wikipedia(object):
    session = requests.Session
    api_url = "https://en.wikipedia.org/w/api.php"

    def get_by_coordinates(self, latitude, longitude):
        params = dict(
            action="query",
            format="json",
            generator="geosearch",
            prop="coordinates",
            ggscoord="{}|{}".format(latitude, longitude),
        )
        resp = self.session.get(url=self.api_url, params=params)

        return resp.json()
