import pprint

from django.db.models import DateTimeField
from gis.models import PostalCode, AbstractStreetAddress

from app.geonames_class import GeoNames


class Point(AbstractStreetAddress):
    time = DateTimeField(null=True)

    def reverse_geocode(self, commit=True):
        if not self.address1 or not self.state or not self.zip_code or not self.postal_code:
            gn = GeoNames(debug=True, username="avryhof")
            gn_result = gn.reverse_geocode(latitude=self.latitude, longitude=self.longitude)

            address = gn_result.get("nearby")
            if not self.address1:
                self.address1 = "%s %s" % (address.get("streetNumber"), address.get("street"))

            if not self.state:
                self.state = address.get("adminCode1")

            if not self.zip_code:
                self.zip_code = address.get("postalcode")

            if not self.postal_code:
                self.link_postal_code()

            if self.postal_code and not self.city:
                self.city = self.postal_code.place_name

        if commit:
            self.save()

    def save(self, *args, **kwargs):
        self.reverse_geocode(commit=False)

        super(Point, self).save(*args, **kwargs)

        self.normalize()
