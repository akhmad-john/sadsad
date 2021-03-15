from django.db import models

from smi.core.models import BaseModel


class Product(BaseModel):
    factory = models.ForeignKey('factory.Factory', on_delete=models.CASCADE, null=True, blank=True, related_name='products')
    mat_id = models.CharField(max_length=18)
    mat_name = models.CharField(max_length=255, null=True, blank=True)
    unit = models.CharField(max_length=128, null=True, blank=True)
    pro_id = models.CharField(max_length=1, null=True, blank=True)
    proid_name = models.CharField(max_length=128, null=True, blank=True)
    mat_type = models.CharField(max_length=4, null=True, blank=True)
    mat_type_name = models.CharField(max_length=128, null=True, blank=True)
    oldmaterial = models.CharField(max_length=18, null=True, blank=True)

    class Meta:
        ordering = (
            'mat_id',
        )
        unique_together = (
            'factory',
            'mat_id',
        )

    def __str__(self):
        return self.mat_id

