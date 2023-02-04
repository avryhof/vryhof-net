from django import forms

from me.models import Member


class EditMeForm(forms.ModelForm):
    date_of_birth = forms.DateField(required=False, widget=forms.DateInput(attrs={"class": "datepicker"}))

    class Meta:
        model = Member
        fields = (
            "photo",
            "prefix",
            "first_name",
            "middle_name",
            "last_name",
            "suffix",
            "address1",
            "address2",
            "city",
            "state",
            "zip_code",
            "plus_four",
            "date_of_birth",
            "phone",
            "phone2",
            "work",
            "cell",
            "email",
            "email_me",
            "call_me",
        )
