from django import forms


class JoinToCourse(forms.Form):
    buy_course = forms.BooleanField(widget=forms.HiddenInput(), initial=True)
    course_id = forms.IntegerField(widget=forms.HiddenInput())


class AddCommentForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea(), label="Задайте вопрос или оставьте комментарий")
