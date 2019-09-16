from django.contrib import admin

from .models import UserBankAccountModel, CurrencyModel, HystoryOperationsModel


@admin.register(UserBankAccountModel)
class UserAccountAdmin(admin.ModelAdmin):
    list_display = ['ip', 'start_date', 'last_access_data']
    ordering = ['ip']


@admin.register(HystoryOperationsModel)
class HystoryOperationsAccountAdmin(admin.ModelAdmin):
    list_display = ['date', 'code', 'currency', 'value']
    ordering = ['date']


@admin.register(CurrencyModel)
class CurrencyAccountAdmin(admin.ModelAdmin):
    list_display = ['currency', 'value']
    ordering = ['value']
