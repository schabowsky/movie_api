from django.conf.urls import url
from django.contrib import admin

from . import views as api_views

urlpatterns = [
    url(r'^movies', api_views.Movies.as_view()),
    url(r'^comments', api_views.Comments.as_view()),
    url(r'^top', api_views.Top.as_view()),
]
