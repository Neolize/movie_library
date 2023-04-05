from django.shortcuts import redirect
from django.views.generic import View
from django.core.handlers.wsgi import WSGIRequest

from mailing.forms import MailingForm
from mailing.services import UserEmailCreation


class MailingView(View):
    """Рассылка по email"""
    form = MailingForm

    def post(self, request: WSGIRequest):
        user_email_creation_obj = UserEmailCreation(form=self.form(request.POST))
        user_email_creation_obj.save_user_email()
        return redirect(to='home')
