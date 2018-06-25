from django.conf.urls import url, include
from .views import *

urlpatterns = [
    url(r'^list', PayrollListView.as_view(), name='list'),
    url(r'^(?P<pk>[0-9]+)/$', PayrollDetailView.as_view(), name='detail'),
    url(r'^entry/$', PayrollEntryView.as_view(), name='entry'),
    url(r'^(?P<pk>[0-9]+)/review/$', PayrollReviewView.as_view(), name='review'),
]
