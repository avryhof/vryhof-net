from django import forms


class LoginForm(forms.Form):
    username = forms.CharField(label="Username or Email address", max_length=100)


class LoginTokenForm(forms.Form):
    token = forms.CharField(label="Login Token", max_length=64)
