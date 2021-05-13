from django.conf import settings
from rest_framework import serializers
from django_auth.models import TestAccess

class TestAccessSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestAccess
        fields = "__all__"