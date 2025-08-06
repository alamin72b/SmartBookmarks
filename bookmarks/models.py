from __future__ import annotations
from django.db import models
from django.urls import reverse

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    parent = models.ForeignKey(
        "self", null=True, blank=True, on_delete=models.SET_NULL, related_name="children"
    )
    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    def __str__(self):
        return self.name


class Bookmark(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    category = models.ForeignKey(Category, null=True, blank=True, on_delete=models.SET_NULL)
    tags = models.ManyToManyField(Tag, blank=True)
    text = models.TextField(blank=True)
    embedding = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    view_count = models.PositiveIntegerField(default=0)  # Track views
    def __str__(self):
        return self.title
    def get_absolute_url(self):
        return reverse('bookmark_detail', kwargs={'pk': self.pk})


class BookmarkFile(models.Model):
    bookmark = models.ForeignKey(Bookmark, related_name="files", on_delete=models.CASCADE)
    file = models.FileField(upload_to="uploads/")
    def __str__(self):
        return self.file.name


# New Model to Handle Multiple URLs for Each Bookmark
class BookmarkLink(models.Model):
    bookmark = models.ForeignKey(Bookmark, related_name="links", on_delete=models.CASCADE)
    url = models.URLField()
    def __str__(self):
        return self.url
