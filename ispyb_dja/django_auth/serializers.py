from rest_framework import serializers

from ispyb_dja.django_auth.models import TestAccess


class TestAccessSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestAccess
        fields = "__all__"
