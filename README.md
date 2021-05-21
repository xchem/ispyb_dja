# Authentication and authorization for XChem Web Apps
This repo contains everything you need to implement authentication (via CAS) and authorization (via ISPyB) for a web app
with a django & django REST framework back-end that you want to connect to Diamond data

## Installation

```pip install ispyb_dja```

## Usage

### Edit settings.py
Add `ispyb_dja`, `django_cas_ng` and `guardian` to your apps `settings.py` file in the `INSTALLED_APPS` section:

```python
INSTALLED_APPS = [
    "my_app",
    "ispyb_dja",
    '...',
    "django_cas_ng",
    "guardian"
]
```

Add the following settings to your apps `settings.py` file, changing them where appropriate

```python
# CAS parameters
CAS_SERVER_URL = "https://auth.diamond.ac.uk:443/cas/"
# Where to redirect to after user has logged in with CAS
CAS_REDIRECT_URL = "/"
CAS_FORCE_CHANGE_USERNAME_CASE = "lower"

AUTHENTICATION_BACKENDS = (
    "django.contrib.auth.backends.ModelBackend",
    "django_cas_ng.backends.CASBackend",
    "guardian.backends.ObjectPermissionBackend",
)
LOGIN_URL = "/accounts/login/"
LOGOUT_URL = "/accounts/logout/"
```

You may have to ask for your applications URL to be added to a list of allowed urls for CAS to work in production

### Set environment variables/secrets 
Set the following environment variables as secrets (they are secrets, so make sure they stay that way!)

```
ISPYB_USER=<Your ISPyB username>
ISPYB_PASSWORD=<Your ISPyB password>
ISPYB_HOST=<ispyb host address>
ISPYB_PORT=<ispyb port>
SECURITY_CONNECTOR=<ssh_ispyb for remote or ispyb for local>
```

If your app is running outside of Diamond, you will also need:

```
SSH_HOST=ssh.diamond.ac.uk
SSH_USER=<username for ssh into diamond>
SSH_PASSWORD=<password for ssh into diamond>
```

### Use the ISPyB-DJA authorization model to define projects linked to proposals/visits
Use the `django_auth.models.IspybAuthorization` model to connect any sensitive data via. foreign key. 

For example:

```python
from ispyb_dja.django_auth.models import IspybAuthorization
from django.db import models

class SensitiveData(models.Model):
    related_project = models.ForeignKey(IspybAuthorization, on_delete=models.CASCADE)
    sensitive_data = models.CharField(max_length=200, unique=False)

```

The IspybAuthorization model includes three fields:
- project - a charfield that you can use to give a project in your app a name
- proposal_visit - the proposal number and visit that the data/project are related to (e.g. lb13385-10)
- users - a ManyToMany field that is used by the authentication layer. Ignore this

So to create a new project and link our sensitive data, an example might be:

```python
from ispyb_dja.django_auth.models import IspybAuthorization
from my_app.models import SensitiveData

new_project = IspybAuthorization(project='A sensitive bit of data', proposal_visit='lb13385-10')
new_data = SensitiveData(related_project=new_project, sensitive_data='something secret')
```

### Use the IspybSafeQuerySet to secure serializers/views and provide authorization
To use the ISPyB-DJA authorization feature, instead of using a django or DRF view class, you use the custom 
`IspybSafeQuerySet` in your `views.py` file:

```python
from ispyb_dja.ispyb_auth.ispyb_djangoauth import ISpyBSafeQuerySet
from my_app.models import SensitiveData
from my_app.serializers import SensitiveDataSerializer

class TestAccessView(ISpyBSafeQuerySet):
    queryset = SensitiveData.objects.filter()
    serializer_class = SensitiveDataSerializer
    filter_permissions = "related_project_id"
    filter_fields = ("sensitive_data",)
```
where `filter_permissions` tells us which foreign key field in your model links to the `IspybAuthorization` model

### Add login and logout urls to urls.py

```python
url(r"^accounts/login/", django_cas_ng.views.LoginView.as_view(), name="cas_ng_login"),
    url(r"^accounts/logout/", django_cas_ng.views.LogoutView.as_view(), name="cas_ng_logout"),
    url(
        r"^accounts/callback$",
        django_cas_ng.views.CallbackView.as_view(),
        name="cas_ng_proxy_callback",
    ),
```
