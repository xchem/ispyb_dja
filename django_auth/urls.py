"""ispyb-djangoauth URL Configuration
The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from django.conf.urls import url
from . import views
import django_cas_ng.views
from django.views.generic.base import RedirectView

urlpatterns = [
    url(r'admin/', admin.site.urls),
    url(r'test_access/', views.TestAccessView.as_view({'get': 'list'}), name="test_access"),
    url(r"^accounts/login/", django_cas_ng.views.LoginView.as_view(), name="cas_ng_login"),
    url(r"^accounts/logout/", django_cas_ng.views.LogoutView.as_view(), name="cas_ng_logout"),
    url(
        r"^accounts/callback$",
        django_cas_ng.views.CallbackView.as_view(),
        name="cas_ng_proxy_callback",
    ),
    url(r"^$", RedirectView.as_view(url="/test_access/")),
]
