from django.db import models

from smi.core.models import BaseModel
from smi.movement import MovementLogStatus, TransferLogStatus


class IdCard(BaseModel):
    factory = models.ForeignKey('factory.Factory', related_name='id_cards', on_delete=models.CASCADE)
    card_number = models.CharField(max_length=20, null=True, blank=True)
    name = models.CharField(max_length=128, null=True, blank=True)

    class Meta:
        unique_together = (
            'factory',
            'card_number',
        )

    def __str__(self):
        return f'{self.card_number} - {self.name}'


class ProductMovement(BaseModel):
    zone_from = models.ForeignKey('zone.Zone', related_name='zone_from_set', on_delete=models.CASCADE)
    zone_to = models.ForeignKey('zone.Zone', related_name='zone_to_set', on_delete=models.CASCADE)
    card_om = models.ForeignKey(IdCard, related_name='card_om_set', on_delete=models.SET_NULL, null=True, blank=True)
    card_pm = models.ForeignKey(IdCard, related_name='card_pm_set', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ('updated_at',)
        unique_together = (
            'zone_from',
            'card_om',
            'zone_to',
            'card_pm'
        )


class MovementLog(BaseModel):
    factory = models.CharField(max_length=10, null=True, blank=True)
    zone = models.CharField(max_length=30, null=True, blank=True)
    status = models.CharField(max_length=50, choices=MovementLogStatus.CHOICES, null=True, blank=True)
    message = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = 'Mes Get Product Log'
        verbose_name_plural = 'Mes Get Product Logs'

    def __str__(self):
        return self.status


class TransferLog(BaseModel):
    factory_from = models.CharField(max_length=10, null=True, blank=True)
    factory_to = models.CharField(max_length=10, null=True, blank=True)
    zone_from = models.CharField(max_length=30, null=True, blank=True)
    zone_to = models.CharField(max_length=30, null=True, blank=True)
    postingdate = models.CharField(max_length=30, null=True, blank=True)
    requestdate = models.CharField(max_length=30, null=True, blank=True)
    card_from = models.CharField(max_length=20, null=True, blank=True)
    card_to = models.CharField(max_length=20, null=True, blank=True)
    status = models.CharField(max_length=50, choices=TransferLogStatus.CHOICES, null=True, blank=True)
    message = models.TextField(null=True, blank=True)

    class Meta:
        verbose_name = 'Mes Send Product Log'
        verbose_name_plural = 'Mes Send Product Logs'

    def __str__(self):
        return str(self.id)


class LogMaterial(BaseModel):
    transfer_log = models.ForeignKey(TransferLog, on_delete=models.CASCADE, related_name="log_materials")
    material = models.CharField(max_length=128, null=True, blank=True)
    materialquan = models.CharField(max_length=50, null=True, blank=True)


class ProductMovementFile(BaseModel):
    file = models.ForeignKey('document.DocumentModel', on_delete=models.SET_NULL, blank=True, null=True)
    errors = models.JSONField(blank=True, null=True)


class IdCardFile(BaseModel):
    file = models.ForeignKey('document.DocumentModel', on_delete=models.SET_NULL, blank=True, null=True)
    errors = models.JSONField(blank=True, null=True)

