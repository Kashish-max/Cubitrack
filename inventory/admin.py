from django.contrib import admin
from .models import Box


class BoxAdmin(admin.ModelAdmin):
    list_display = ('id', 'creator', 'created_on', 'updated_on')
    readonly_fields = ['creator', 'created_on',]

    # set creator to the current user
    def save_model(self, request, obj, form, change):
        # only set creator during the first save.
        if not change:
            obj.creator = request.user
        super().save_model(request, obj, form, change)

admin.site.register(Box, BoxAdmin)
