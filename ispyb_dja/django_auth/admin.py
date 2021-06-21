from django.contrib import admin

from ispyb_dja.django_auth.models import IspybAuthorization, TestAccess

admin.site.register(IspybAuthorization)
admin.site.register(TestAccess)
