from django import forms
from django.contrib.auth import password_validation
from django.contrib.auth.models import User


class RestorePassword(forms.Form):
    email = forms.EmailField()


class RegistrationForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""

    login = forms.CharField(label="E-mail*")
    fio = forms.CharField(label="Имя*")
    password = forms.CharField(widget=forms.PasswordInput, label="Придумайте пароль")


class LoginForm(forms.Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label_suffix = ""

    login = forms.CharField(label="E-mail")
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")


class UserUpdateForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].required = False
        self.fields['password2'].required = False
        self.label_suffix = ""

    password1 = forms.CharField(
        label="Пароль",
        strip=False,
        widget=forms.PasswordInput(attrs={'autocomplete': 'new-password', 'placeholder': 'тут можно поменять пароль'}),
    )
    password2 = forms.CharField(
        label="Пароль ещё раз",
        widget=forms.PasswordInput(attrs={"autocomplete": "new-password", 'placeholder': 'такой же'}),
        strip=False,
    )
    first_name = forms.CharField(
        label="Имя",
    )

    def clean(self):
        """Проверка на совпадение введенных паролей и остальное"""
        cleaner_data = super().clean()
        password = cleaner_data.get("password1")
        password_2 = cleaner_data.get("password2")
        if (len(password) > 0 or len(password_2) > 0) and (password != password_2):
            self.add_error("password1", "Для смены пароля введите новый пароль два раза")
        return cleaner_data

    class Meta:
        model = User
        fields = ["first_name"]
