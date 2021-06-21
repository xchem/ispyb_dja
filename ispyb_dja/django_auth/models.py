from django.contrib.auth.models import User
from django.db import models

class IspybAuthorization(models.Model):
    project = models.CharField(max_length=200, unique=True)
    proposal_visit = models.CharField(max_length=200, unique=True)
    users = models.ManyToManyField(User)

    class Meta:
        unique_together = ('project', 'proposal_visit')

class TestAccess(models.Model):
    username = models.CharField(max_length=200, unique=False)
    project = models.ForeignKey(IspybAuthorization, on_delete=models.SET_NULL, null=True)

    class Meta:
        unique_together = ('username', 'project')