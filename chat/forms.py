from django import forms


class MessageForm(forms.Form):
    text = forms.CharField(
        validators=[],
    )

