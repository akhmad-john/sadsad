from django.contrib.auth.models import AbstractUser, Permission
from django.db import models


class Role(models.Model):
    name = models.CharField(max_length=32, unique=True)
    display_name = models.CharField(max_length=255, blank=True, null=True)
    permissions = models.ManyToManyField(Permission, blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    class Meta:
        ordering = ('name',)

    def __str__(self):
        full_path = [self.name]
        k = self.parent
        while k is not None:
            full_path.append(k.name)
            k = k.parent
        return ' -> '.join(full_path[::-1])


class User(AbstractUser):
    factories = models.ManyToManyField('factory.Factory', blank=True, related_name='users')
    full_name = models.CharField(max_length=256, blank=True, null=True)
    current_password = models.CharField(max_length=250, blank=True, null=True)
    is_mes = models.BooleanField(default=False)
    roles = models.ManyToManyField(Role, related_name='users', blank=True)

    def __str__(self):
        return self.username

    @property
    def get_full_name(self):
        if not self.first_name or not self.last_name:
            full_name = self.username
        else:
            full_name = f"{self.last_name} {self.first_name}"
        return full_name
