from django.urls import path

from mailing.views import MailingView

urlpatterns = [
    path('', MailingView.as_view(), name='mailing'),
]

