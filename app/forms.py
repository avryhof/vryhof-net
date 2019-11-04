from django.forms import ModelForm, CharField, DecimalField, ModelChoiceField

from app.models import Point


class PointForm(ModelForm):
    latitude = DecimalField(max_digits=22, decimal_places=16, required=False, label="Latitude")
    longitude = DecimalField(max_digits=22, decimal_places=16, required=False, label="Longitude")
    name = CharField(max_length=180, required=False, label="Name")
    address1 = CharField(max_length=255, required=False, label="Address1")
    address2 = CharField(max_length=255, required=False, label="Address2")
    city = CharField(max_length=180, required=False, label="City")
    state = CharField(max_length=20, required=False, label="State")
    zip_code = CharField(max_length=20, required=False, label="Zip code")

    class Meta:
        model = Point

    def save(self, commit=True):
        super(PointForm, self).save(commit=commit)

        meta = getattr(self, "Meta", None)
        if meta:
            model = getattr(meta, "model", False)

            if model:
                if not model.latitude and not model.longitude:
                    model.geocode()
                else:
                    model.normalize()

                model.link_postal_code()



