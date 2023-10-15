from django.forms import Form, CharField, DateField, DateInput, BooleanField, IntegerField


class MemberSearchForm(Form):
    search_terms = CharField(required=True, label="Find Member")


class MemberTypeForm(Form):
    first_name = CharField(required=False, label="First Name")
    last_name = CharField(required=False, label="Last Name")
    date_of_birth = DateField(
        required=False,
        label="Date of Birth",
        widget=DateInput(attrs={"class": "form-control", "placeholder": "mm/dd/yyyy"}),
    )
    zip_code = CharField(required=False, label="Zip Code")


class account_choose(Form):
    user_id = IntegerField()


class UserLinkForm(Form):
    find_user = CharField(required=True, label="Find User")
