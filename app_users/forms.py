from django import forms


class RestorePassword(forms.Form):
    email = forms.EmailField()


class LoginForm(forms.Form):
    login = forms.CharField(label="Имя пользователя или емейл")
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")
