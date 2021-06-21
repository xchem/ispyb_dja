from django.contrib.auth.models import User
from rest_framework.test import APIRequestFactory, force_authenticate, APITestCase

from django_auth.models import TestAccess
from django_auth.views import TestAccessView
from ispyb_auth.ispyb_djangoauth import *


class IspybAuthTestCase(APITestCase):

    def setUp(self):
        self.factory = APIRequestFactory()
        self.authenticated_user = User.objects.create(username=os.environ.get('TEST_USER'), password='DUMMY')
        self.fake_user = User.objects.create(username='NOTAUSER', password='DUMMY')
        self.view = TestAccessView.as_view({'get': 'list'})
        self.request = self.factory.get('/test_access/')

    def test_0_authenticated(self):

        test_auth_entry = IspybAuthorization.objects.get_or_create(project=os.environ.get('TEST_PROJECT'),
                                                                   proposal_visit=os.environ.get(
                                                                       'TEST_PROPOSAL_VISIT'))[0]
        test_access_entry = TestAccess.objects.get_or_create(
            username=os.environ.get('TEST_USER'), project=test_auth_entry
        )[0]

        force_authenticate(self.request, user=self.authenticated_user)
        response = self.view(self.request)
        response.render()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('ascii'),
                         '[{"id":1,"username":"' + os.environ.get('TEST_USER') + '","project":1}]')

    def test_1_fake_visit(self):
        test_non_auth_entry = IspybAuthorization.objects.get_or_create(
            project='notarealproject', proposal_visit="notarealvisit"
        )[0]
        test_access_denied = TestAccess(username=os.environ.get('TEST_USER'), project=test_non_auth_entry)

        force_authenticate(self.request, user=self.authenticated_user)
        response = self.view(self.request)
        response.render()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('ascii'), '[]')

    def test_2_fake_user(self):
        test_auth_entry = IspybAuthorization.objects.get_or_create(project=os.environ.get('TEST_PROJECT'),
                                                                   proposal_visit=os.environ.get(
                                                                       'TEST_PROPOSAL_VISIT'))[0]
        test_access_entry = TestAccess.objects.get_or_create(
            username=os.environ.get('TEST_USER'), project=test_auth_entry
        )[0]

        force_authenticate(self.request, user=self.fake_user)
        response = self.view(self.request)
        response.render()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode('ascii'), '[]')

