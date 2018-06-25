from django.conf.urls import url, include
from .views import ProfileCreateView

urlpatterns = [
    url(r'^signup', ProfileCreateView.as_view(), name='signup'),
]