"""sebastien URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.urls import reverse_lazy
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.views.generic import TemplateView
from django.views.generic.base import RedirectView

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='__base.html'), name='home'),
    url(r'^admin/', admin.site.urls),
    url(r'^payroll/', include(('payroll.urls', 'payroll'), namespace='payroll')),
    url(r'^payroll/$',RedirectView.as_view(url=reverse_lazy('payroll:list')), name='payroll_redirect'),
    url(r'^accounts/', include(('profiles.urls', 'profiles'), namespace='profile')),
    url(r'^accounts/login/$', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    url(r'^accounts/logout/$', auth_views.logout, {'next_page': 'home'}, name='logout'),
]
