from django import forms


class RestorePassword(forms.Form):
    email = forms.EmailField()
