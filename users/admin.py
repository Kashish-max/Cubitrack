from django.contrib import admin
from .models import User

from rest_framework_simplejwt.token_blacklist.admin import OutstandingTokenAdmin
from rest_framework_simplejwt.token_blacklist import models


class CustomOutstandingTokenAdmin(OutstandingTokenAdmin):

    def has_delete_permission(self, *args, **kwargs):
        return True

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_superuser',)
    exclude = ('password',)
    readonly_fields = ('verification_token', 'token_created_at')

admin.site.register(User, UserAdmin)

admin.site.unregister(models.OutstandingToken)
admin.site.register(models.OutstandingToken, CustomOutstandingTokenAdmin)
