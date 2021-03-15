from django.db import models

from smi.core.models import BaseModel


class Factory(BaseModel):
    plant_id = models.PositiveIntegerField("завод номер", unique=True)
    plantname = models.CharField("Наименование завода", max_length=128, null=True, blank=True)
    firmtext = models.CharField(max_length=128, null=True, blank=True)
    factory_link = models.CharField(max_length=500, null=True, blank=True)  # link of mes
    tex_link = models.CharField(max_length=500, null=True, blank=True)

    class Meta:
        ordering = ('plantname',)

    def __str__(self):
        return f'{self.id}. {self.plant_id} - {self.plantname}'
