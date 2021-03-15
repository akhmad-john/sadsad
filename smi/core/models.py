from django.db import models

from smi.core.utils.utils import get_current_user


class BaseModel(models.Model):
    create_by = models.ForeignKey('account.User', on_delete=models.SET_NULL, related_name='%(class)s_created',
                                  blank=True, null=True)
    update_by = models.ForeignKey('account.User', on_delete=models.SET_NULL, related_name='%(class)s_modified',
                                  blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True
        ordering = ('-created_at',)

    def save(self, *args, **kwargs):
        user = get_current_user()
        if user and user.is_authenticated:
            self.update_by = user
            if not self.id:
                self.create_by = user
        super(BaseModel, self).save(*args, **kwargs)

    def has_changes(self, **kwargs):
        return any(getattr(self, field) != value for field, value in kwargs.items())

    def save_changes_if_has(self, **kwargs):
        if self.has_changes(**kwargs):
            for field, value in kwargs.items():
                setattr(self, field, value)
            self.save()


class StatusModelMixin(models.Model):
    status = None
    __old_status = None

    class Meta:
        abstract = True

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__old_status = self.status

    @property
    def status_is_change(self):
        return self.status != self.__old_status

    @status_is_change.setter
    def status_is_change(self, value):
        self.__old_status = self.status if not value else None

