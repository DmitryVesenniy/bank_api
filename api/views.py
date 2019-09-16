from django.contrib.auth.models import User

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework import permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status


from .serializers import UserSerializer, UserBalanceSerializer, UserDepositSerializer
from .models import CURRENCY_CODE_FORW, CURRENCY_CODE_BACK, CURRENCY_MINIMAL_VALUE, CURRENCY_VALUES


@api_view(['POST'])
@permission_classes((AllowAny,))
def register(request):
    ip = request.META.get('REMOTE_ADDR', '') or request.META.get('HTTP_X_FORWARDED_FOR', '')

    serialized = UserSerializer(data=request.data)
    if serialized.is_valid():
        user = serialized.create(ip=ip)
        return Response(UserSerializer(instance=user).data, status=status.HTTP_201_CREATED)

    else:
        return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)


class BalanceUserView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        return Response({"detail":"Метод \"GET\" не разрешен."})

    def post(self, request, *args, **kwargs):

        balances = request.user.userbankaccountmodel.balance.all().\
            values("id", "currency", "value",)

        for balance in balances:
            cur_code = balance["currency"]
            value = balance["value"]

            balance["currency"] = CURRENCY_CODE_BACK[cur_code]
            balance["value"] = value / CURRENCY_MINIMAL_VALUE[balance["currency"]]

        return Response(balances, status=status.HTTP_200_OK)


class DepositView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        serializer = UserDepositSerializer(data=request.data)

        if serializer.is_valid():
            try:
                res = serializer.save(request.user)

            except (TypeError, KeyError):
                return Response({"success": False, "error": "type_error"}, status=status.HTTP_400_BAD_REQUEST)

            return Response(res, status=status.HTTP_200_OK)

        return Response({"success": False, "error": "not_valid"}, status=status.HTTP_400_BAD_REQUEST)


class WithdrawView(APIView):
    permission_classes = (permissions.IsAuthenticated,)

    def post(self, request, *args, **kwargs):

        try:
            currency = CURRENCY_CODE_FORW[request.data["currency"]]
            money_withdraw = int(request.data["amount"])
            value = money_withdraw * CURRENCY_MINIMAL_VALUE[request.data["currency"]]

        except (TypeError, KeyError):
            return Response({"success": False, "error": "key_error"}, status=status.HTTP_400_BAD_REQUEST)

        user_account = request.user.userbankaccountmodel

        balances = user_account.balance.filter(currency=currency)

        if len(balances) == 0 or balances[0].value < value:
            return Response({"success": False, "error": "insufficient_funds"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = UserDepositSerializer(data=request.data)
        data = serializer.update(request.user, balances[0], {"value": value * -1, "currency": currency})

        result = get_amounts(money_withdraw, CURRENCY_VALUES[currency])

        data["result"] = result

        return Response(data, status=status.HTTP_200_OK)


# utils function
def get_amounts(money, currency_values):
    data = []
    for index, amount in enumerate(currency_values[::-1]):
        value = money // amount
        if money // amount > 0:
            data.append({"value": amount, "quantity": value})
            money -= amount * value
            if money == 0:
                return data
