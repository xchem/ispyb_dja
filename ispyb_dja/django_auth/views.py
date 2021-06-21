from django_auth.models import TestAccess
from django_auth.serializers import TestAccessSerializer
from ispyb_auth.ispyb_djangoauth import ISpyBSafeQuerySet


class TestAccessView(ISpyBSafeQuerySet):
    queryset = TestAccess.objects.filter()
    serializer_class = TestAccessSerializer
    filter_permissions = "project_id"
    filter_fields = ("username",)
