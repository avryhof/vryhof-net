from django.forms import Form, CharField, TextInput, DecimalField


class CacheSearchForm(Form):
    terms = CharField(required=False, label="Search", widget=TextInput())
    latitude = CharField(required=False)
    longitude = CharField(required=False)
    radius = DecimalField(required=False)
