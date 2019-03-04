from django.db import models
from django.contrib.postgres.fields import JSONField

class Movie(models.Model):
    title = models.CharField(max_length=50, null=True, blank=True)
    data = JSONField()


class Comment(models.Model):
    ts = models.DateTimeField(auto_now_add=True, editable=False, null=False, blank=False)
    body = models.CharField(max_length=500, null=True, blank=True)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
