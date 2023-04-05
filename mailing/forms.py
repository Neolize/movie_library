from django import forms
from snowpenguin.django.recaptcha3.fields import ReCaptchaField

from mailing.models import Mailing


class MailingForm(forms.ModelForm):
    """Форма подписки на email рассылку"""
    recaptcha = ReCaptchaField()

    class Meta:
        model = Mailing
        fields = ('email', 'recaptcha')
        widgets = {
            'email': forms.TextInput(attrs={'class': 'editContent', 'placeholder': 'Enter your email...',
                                            'style': 'width: 250px; padding-left: 10px;'})
        }
        labels = {
            'email': '',
        }
