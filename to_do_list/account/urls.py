from django.conf.urls import re_path, include
from account.views import dashboard, register

app_name = 'account'

urlpatterns = [
    # re_path(r"^dashboard/", dashboard, name="dashboard"),
    re_path(r"^accounts/", include("django.contrib.auth.urls")),
    re_path(r"^register/", register, name="register"),
]