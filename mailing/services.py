from mailing.forms import MailingForm


class UserEmailCreation:
    """Добавление email-а пользователя"""
    def __init__(self, form: MailingForm):
        self.form = form

    def __check_form(self) -> bool:
        if self.form.is_valid():
            return True
        return False

    def save_user_email(self) -> None:
        if self.__check_form():
            self.form.save()
