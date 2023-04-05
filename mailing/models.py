from django.db import models


class Mailing(models.Model):
    """Email рассылка"""
    email = models.EmailField()
    subscribe_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

    class Meta:
        db_table = 'Mailing'
        ordering = ['id']
