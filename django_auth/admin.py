from django.contrib import admin
from django_auth.models import IspybAuthorization, TestAccess

admin.site.register(IspybAuthorization)
admin.site.register(TestAccess)
