from django.db import models

from smi.core.models import BaseModel, StatusModelMixin
from smi.order import OrderStatus, OrderCheckStatus, NoKonvOrderCloseStatus, KonvOrderCloseStatus


class Order(StatusModelMixin, BaseModel):
    factory = models.ForeignKey('factory.Factory', on_delete=models.SET_NULL, related_name='orders', null=True,
                                blank=True)
    aufnr = models.CharField(max_length=12, null=True, blank=True)
    product = models.ForeignKey('product.Product', on_delete=models.SET_NULL, related_name='orders', null=True,
                                blank=True)
    zone = models.ForeignKey('zone.Zone', on_delete=models.SET_NULL, null=True, blank=True, related_name='orders')
    psmng = models.DecimalField(decimal_places=3, max_digits=13, null=True, blank=True)
    status = models.CharField(max_length=50, choices=OrderStatus.CHOICES, default=OrderStatus.CREATED)
    counter = models.DecimalField(decimal_places=3, max_digits=13, default=0.00)
    cycle = models.CharField(max_length=128, null=True, blank=True)
    cycleunit = models.CharField(max_length=128, null=True, blank=True)
    active = models.BooleanField(default=False)
    order_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name = "Create order"
        verbose_name_plural = "Create orders"

    @property
    def is_editable(self):
        return self.counter == 0

    @staticmethod
    def report_cols():
        cols = {
            'id': 'Номер заказа SMI',
            'aufnr': 'Номер заказа SAP',
            'status': 'Журнал',
            'active': 'Статус',
            'created_at': 'Дата создания',
            'order_date': 'Дата заказа',
            'product__mat_id': 'Код материала',
            'product__mat_name': 'Наименование материала',
            'cycle': 'Время цикла',
            'cycleunit': 'Eдиница цикла',
            'product__mat_type_name': "Вид материала",
            'product__unit': 'Ед.изм',
            'zone__zonename': 'Участок',
            'zone__p_number': 'Номер панели',
            'zone__ip_address': 'IP адрес',
            'psmng': 'План количество',
            'counter': 'Факт количество',
            'result': 'Разница П/Ф',
        }
        return cols


class Log(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='logs', null=True, blank=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    message = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ('-created_at',)
        verbose_name = "Create log"
        verbose_name_plural = "Create logs"

    def __str__(self):
        return f'{self.id}'


class OrderCheck(BaseModel):
    factory = models.ForeignKey('factory.Factory', on_delete=models.SET_NULL, null=True, blank=True)
    product = models.ForeignKey('product.Product', on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=50, choices=OrderCheckStatus.CHOICES)
    message = models.TextField()
    active = models.BooleanField(default=False)
    sap_message = models.TextField(default="")


class NeKonvOrderClose(BaseModel):
    aufnr = models.CharField(max_length=12, null=True, blank=True)
    quantity = models.CharField(max_length=128, null=True, blank=True)
    status = models.CharField(max_length=50, choices=NoKonvOrderCloseStatus.CHOICES, null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    data = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f'id: {self.id}'


class NeKonvOrderCloseReport(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, null=True, blank=True)
    quantity = models.CharField(max_length=128, null=True, blank=True)
    zone = models.ForeignKey('zone.Zone', on_delete=models.SET_NULL, null=True, blank=True)
    product = models.ForeignKey('product.Product', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f'id: {self.id}'


class KonvOrderClose(BaseModel):

    ipaddress = models.CharField(max_length=50, null=True, blank=True)
    p_number = models.CharField(max_length=20, null=True, blank=True)
    serialnum = models.CharField(max_length=5000, null=True, blank=True)
    status = models.CharField(max_length=50, choices=KonvOrderCloseStatus.CHOICES, null=True, blank=True)
    message = models.TextField(null=True, blank=True)
    data = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f'id: {self.id}'


class TrashOrderClose(BaseModel):
    message = models.TextField(null=True, blank=True)
    data = models.JSONField(null=True, blank=True)

    class Meta:
        ordering = ('-created_at',)

    def __str__(self):
        return f'id: {self.id}'

