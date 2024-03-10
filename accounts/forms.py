from django import forms

from accounts.models import UserPrefs


class LoginForm(forms.Form):
    username = forms.CharField(label="Username or Email address", max_length=100)


class LoginTokenForm(forms.Form):
    token = forms.CharField(label="Login Token", max_length=64)


class UserPreferencesEditForm(forms.ModelForm):
    class Meta:
        model = UserPrefs
        fields = ["first_name", "last_name", "email", "photo"]
