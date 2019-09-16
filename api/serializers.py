from django.contrib.auth import get_user_model

from rest_framework import serializers

from .models import DEPOSIT, CASH_WITHDRAWAL, CURRENCY_CODE_FORW, CURRENCY_MINIMAL_VALUE, CurrencyModel, HystoryOperationsModel


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    user_model = get_user_model()

    def create(self, *args, **kwargs):
        user = self.user_model.objects.create(**self.validated_data)
        user.set_password(self.validated_data['password'])
        user.userbankaccountmodel.ip = kwargs.get("ip", "-")
        user.save()

        return user

    class Meta:
        model = get_user_model()
        fields = ("id", "username", "password",)


class UserBalanceSerializer(serializers.Serializer):
    currency = serializers.CharField(max_length=10)
    value = serializers.CharField(max_length=100)


class UserDepositSerializer(serializers.Serializer):
    currency = serializers.CharField(max_length=10)
    value = serializers.IntegerField()
    quantity = serializers.IntegerField()

    def save(self, user):
        currency = self.validated_data["currency"]
        value = self.validated_data["value"] * CURRENCY_MINIMAL_VALUE[currency]
        quantity = self.validated_data.get("quantity", 1)
        user_account = user.userbankaccountmodel

        user_balance = user_account.balance.filter(currency=CURRENCY_CODE_FORW[currency])
        history = HystoryOperationsModel.objects.create(code=DEPOSIT, value=value, currency=CURRENCY_CODE_FORW[currency])

        if len(user_balance) > 0:
            balance = user_balance[0]

            balance.value += value * quantity
            balance.save()

        else:
            balance = CurrencyModel.objects.create(currency=CURRENCY_CODE_FORW[currency], value=value * quantity)
            user_account.balance.add(balance)

        user_account.hystory.add(history)
        user.save()

        return {"success": True}

    def update(self, user, balance, validated_data):
        balance.value += validated_data["value"]
        balance.save()

        history = HystoryOperationsModel.objects.create(code=CASH_WITHDRAWAL, value=validated_data["value"],
                                                        currency=validated_data["currency"])

        user_account = user.userbankaccountmodel
        user_account.hystory.add(history)
        user.save()

        return {"success": True}
