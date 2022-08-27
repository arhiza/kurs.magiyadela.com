from django import forms


class JoinToCourse(forms.Form):
    buy_course = forms.BooleanField(widget=forms.HiddenInput(), initial=True)
    course_id = forms.IntegerField(widget=forms.HiddenInput())