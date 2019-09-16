from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from django.contrib.auth.models import User


RUB = 0
USD = 1
EUR = 2

CURRENCY_CODE = (
    (RUB, "Рубли"),
    (USD, "Доллары"),
    (EUR, "Евро")
)

CURRENCY_CODE_FORW = {
    "RUB": RUB,
    "USD": USD,
    "EUR": EUR,
}

CURRENCY_CODE_BACK = {
    RUB: "RUB",
    USD: "USD",
    EUR: "EUR",
}

CURRENCY_MINIMAL_VALUE = {
    "RUB": 100,
    "USD": 100,
    "EUR": 100,
}

CASH_WITHDRAWAL = 0
DEPOSIT = 1
BALANCE_CHECK = 2

OPERATION_CHOICES = (
    (CASH_WITHDRAWAL, "Снятие наличных"),
    (DEPOSIT, "Пополнение счета"),
    (BALANCE_CHECK, "Проверка баланса")
)

CURRENCY_VALUES = {
    RUB: [1, 5, 10, 50, 100, 500, 1000, 5000],
    USD: [1, 5, 10, 50, 100, 500, 1000, 5000],
    EUR: [1, 5, 10, 50, 100, 500, 1000, 5000],
}


class HystoryOperationsModel(models.Model):

    date = models.DateTimeField(auto_now=True)
    code = models.IntegerField(verbose_name="Код операации", choices=OPERATION_CHOICES)
    currency = models.IntegerField(verbose_name="Код валюты", choices=CURRENCY_CODE)
    value = models.BigIntegerField(verbose_name="Количество валюты в минимальных единицах")


class CurrencyModel(models.Model):
    currency = models.IntegerField(verbose_name="Код валюты", choices=CURRENCY_CODE)
    value = models.BigIntegerField(verbose_name="Количество валюты в минимальных единицах")

    def save(self, *args, **kwargs):
        if self.value < 0:
            raise NotValidValue

        super(CurrencyModel, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.currency}: {self.value}'


class UserBankAccountModel(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ip = models.CharField(u'IP', max_length=20, null=True, blank=True)
    start_date = models.DateTimeField(auto_now_add=True)
    last_access_data = models.DateTimeField(auto_now=True)
    balance = models.ManyToManyField(CurrencyModel)
    hystory = models.ManyToManyField(HystoryOperationsModel)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserBankAccountModel.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.userbankaccountmodel.save()


# custom exceptions
class NotValidValue(Exception):

    def __init__(self):
        self.value = "Сумма не может быть меньше нуля"

    def __str__(self):
        return repr(self.value)
