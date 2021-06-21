from ispyb_dja.django_auth.models import TestAccess
from ispyb_dja.django_auth.serializers import TestAccessSerializer
from ispyb_dja.ispyb_auth.ispyb_djangoauth import ISpyBSafeQuerySet


class TestAccessView(ISpyBSafeQuerySet):
    queryset = TestAccess.objects.filter()
    serializer_class = TestAccessSerializer
    filter_permissions = "project_id"
    filter_fields = ("username",)
