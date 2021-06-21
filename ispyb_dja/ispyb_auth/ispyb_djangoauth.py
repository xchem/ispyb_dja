import os
import time
from wsgiref.util import FileWrapper

from django.http import Http404
from django.http import HttpResponse
from ispyb import NoResult
from ispyb.connector.mysqlsp.main import ISPyBMySQLSPConnector as Connector
from rest_framework import viewsets

from ispyb_dja.django_auth.models import IspybAuthorization
from .ispyb_remote_connector import IspybSSHConnector

USER_LIST_DICT = {}

connector = os.environ.get('SECURITY_CONNECTOR', 'ispyb')


# example test:
# from rest_framework.test import APIRequestFactory
#
# from rest_framework.test import force_authenticate
# from viewer.views import TargetView
# from django.contrib.auth.models import User
#
# factory = APIRequestFactory()
# view = TargetView.as_view({'get': 'list'})
# user = User.objects.get(username='uzw12877')
# # Make an authenticated request to the view...
# request = factory.get('/api/targets/')
# force_authenticate(request, user=user)
# response = view(request)


def get_remote_conn():
    ispyb_credentials = {
        "user": os.environ["ISPYB_USER"],
        "pw": os.environ["ISPYB_PASSWORD"],
        "host": os.environ["ISPYB_HOST"],
        "port": os.environ["ISPYB_PORT"],
        "db": "ispyb",
        "conn_inactivity": 360,
    }

    ssh_credentials = {
        'ssh_host': os.environ["SSH_HOST"],
        'ssh_user': os.environ["SSH_USER"],
        'ssh_password': os.environ["SSH_PASSWORD"],
        'remote': True
    }

    ispyb_credentials.update(**ssh_credentials)

    conn = IspybSSHConnector(**ispyb_credentials)
    return conn


def get_conn():
    credentials = {
        "user": os.environ["ISPYB_USER"],
        "pw": os.environ["ISPYB_PASSWORD"],
        "host": os.environ["ISPYB_HOST"],
        "port": os.environ["ISPYB_PORT"],
        "db": "ispyb",
    }
    conn = Connector(**credentials)
    return conn


class ISpyBSafeQuerySet(viewsets.ReadOnlyModelViewSet):

    def get_queryset(self):
        """
        Optionally restricts the returned purchases to a given proposals
        """
        # The list of proposals this user can have
        proposal_list = self.get_proposals_for_user()
        # Add in the ones everyone has access to
        proposal_list.extend(self.get_open_proposals())
        # Must have a directy foreign key (project_id) for it to work
        filter_dict = self.get_filter_dict(proposal_list)
        return self.queryset.filter(**filter_dict).distinct()

    def get_open_proposals(self):
        """
        Returns the list of proposals anybody can access
        :return:
        """
        if os.environ.get("TEST_SECURITY_FLAG", False):
            return ["OPEN", "private_dummy_project"]
        else:
            return ["OPEN"]

    def get_proposals_for_user_from_django(self, user):
        # Get the list of proposals for the user
        if user.pk is None:
            return []
        else:
            return list(
                IspybAuthorization.objects.filter(users_id=user.pk).values_list("proposal_visit", flat=True)
            )

    def needs_updating(self, user):
        global USER_LIST_DICT
        update_window = 3600
        if user.username not in USER_LIST_DICT:
            USER_LIST_DICT[user.username] = {"RESULTS": [], "TIMESTAMP": 0}
        current_time = time.time()
        if current_time - USER_LIST_DICT[user.username]["TIMESTAMP"] > update_window:
            USER_LIST_DICT[user.username]["TIMESTAMP"] = current_time
            return True
        return False

    def run_query_with_connector(self, conn, user):
        core = conn.core
        try:
            rs = core.retrieve_sessions_for_person_login(user.username)
            if conn.server:
                conn.server.stop()
        except NoResult:
            rs = []
            if conn.server:
                conn.server.stop()
        return rs

    def get_proposals_for_user_from_ispyb(self, user):
        # First check if it's updated in the past 1 hour
        global USER_LIST_DICT
        if self.needs_updating(user):
            conn = ''
            if connector=='ispyb':
                conn = get_conn()
            if connector=='ssh_ispyb':
                conn = get_remote_conn()

            rs = self.run_query_with_connector(conn=conn, user=user)

            # proposal code = 2 letters (e.g. b); number = 5 numbers (e.g. 13385); session = visit (e.g. 1)
            proposal_visit_ids = list(set([
                x['proposalCode'] + str(x["proposalNumber"]) + "-" + str(x["sessionNumber"]) for x in rs
            ]))
            # prop_ids = list(set([str(x["proposalNumber"]) for x in rs]))
            # prop_ids.extend(visit_ids)
            USER_LIST_DICT[user.username]["RESULTS"] = proposal_visit_ids
            return proposal_visit_ids
        else:
            return USER_LIST_DICT[user.username]["RESULTS"]

    def get_proposals_for_user(self):
        user = self.request.user
        get_from_ispyb = os.environ.get("ISPYB_FLAG", True)
        if get_from_ispyb:
            if user.is_authenticated:
                return self.get_proposals_for_user_from_ispyb(user)
            else:
                return []
        else:
            return self.get_proposals_for_user_from_django(user)

    def get_filter_dict(self, proposal_list):
        # __title_in needs to be replaced with something else e.g. __proposal_visit__in
        return {self.filter_permissions + "__proposal_visit__in": proposal_list}


class ISpyBSafeStaticFiles:

    def get_queryset(self):
        query = ISpyBSafeQuerySet()
        query.request = self.request
        query.filter_permissions = self.permission_string
        query.queryset = self.model.objects.filter()
        queryset = query.get_queryset()
        return queryset

    def get_response(self):
        try:
            queryset = self.get_queryset()
            filter_dict = {self.field_name + "__endswith": self.input_string}
            object = queryset.get(**filter_dict)
            file_name = os.path.basename(str(getattr(object, self.field_name)))

            if hasattr(self, 'file_format'):
                if self.file_format=='raw':
                    file_field = getattr(object, self.field_name)
                    filepath = file_field.path
                    zip_file = open(filepath, 'rb')
                    response = HttpResponse(FileWrapper(zip_file), content_type='application/zip')
                    response['Content-Disposition'] = 'attachment; filename="%s"' % file_name

            else:
                response = HttpResponse()
                response["Content-Type"] = self.content_type
                response["X-Accel-Redirect"] = self.prefix + file_name
                response["Content-Disposition"] = "attachment;filename=" + file_name

            return response
        except Exception:
            raise Http404