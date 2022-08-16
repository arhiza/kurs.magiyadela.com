from django import forms


class RestorePassword(forms.Form):
    email = forms.EmailField()


class LoginForm(forms.Form):
    login = forms.CharField(label="Е-мейл")
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")
