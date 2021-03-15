import os
from django.db import models
from ..core.models import BaseModel


class DocumentModel(BaseModel):
    file = models.FileField(upload_to='documents/')

    class Meta:
        ordering = ('-created_at', )

    def __str__(self):
        return os.path.basename(self.file.name) if self.file else None

    @property
    def file_url(self):
        return self.file.url if self.file else None

    @property
    def file_name(self):
        return os.path.basename(self.file.name) if self.file else None


class ImageModel(models.Model):
    file = models.ImageField(upload_to='images/')
    thumbnail_150 = models.ImageField(upload_to='images/thumbnails_150x150', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at', )

    @property
    def image_url(self):
        return self.file.url if self.file else None
