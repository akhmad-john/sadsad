from django.db import models

from smi.core.models import BaseModel
from smi.zone import ZoneIndicator, ZoneDirection


class Zone(BaseModel):
    factory = models.ForeignKey('factory.Factory', on_delete=models.SET_NULL, related_name='zones', null=True,
                                blank=True, verbose_name="Завод")
    zonename = models.CharField("Наименование склада", max_length=128, null=True, blank=True)
    zone_id = models.PositiveIntegerField("cклад номер")
    indicator = models.CharField(max_length=32, choices=ZoneIndicator.CHOICES, blank=True, null=True)
    head_panel = models.CharField(max_length=20, null=True, blank=True)
    ip_address = models.CharField("IP адрес", max_length=30, null=True, blank=True)
    p_number = models.CharField(max_length=20, null=True, blank=True, unique=True)
    p_name = models.CharField(max_length=128, null=True, blank=True)
    direction = models.CharField(max_length=32, choices=ZoneDirection.CHOICES, blank=True, null=True)
    final_point = models.BooleanField(default=False)

    class Meta:
        ordering = (
            'zonename',
        )
        unique_together = (
            'factory',
            'zonename',
            'zone_id',
            'indicator',
            'head_panel',
            'ip_address',
            'p_number',
        )

    def __str__(self):
        return f'{self.id}.{self.factory.plant_id}/ {self.zone_id} / {self.p_number}'


class ZoneFile(BaseModel):
    file = models.ForeignKey('document.DocumentModel', on_delete=models.SET_NULL, related_name='zone_files',
                             blank=True, null=True)
    errors = models.JSONField(blank=True, null=True)
