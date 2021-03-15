from django.db.models.signals import post_save
from django.dispatch import receiver

from smi.order import OrderStatus
from smi.order.models import Order, Log


@receiver(post_save, sender=Order)
def order_change_receiver(sender, instance, created, **kwargs):
    """

    """
    if instance.status_is_change or created:
        status = instance.status
        if created:
            log_name = 'Плановый заказ в SMI создан'
        # elif None:
        #     log_name = 'Производственный заказ успешно был изменен в SMI'
        elif status in (OrderStatus.SEND, ):
            log_name = "Плановый заказ SMI отправлено в SAP" if not instance.aufnr \
                else "Измененный производственный заказ отправлен в SAP"
        elif status in (OrderStatus.MES_SEND, ):
            log_name = "Производственные заказ SAP отправлено в MES" if getattr(instance, 'mes_update', None) else \
                "Измененный производственный заказ отправлен в MES"
        elif status in (OrderStatus.EDIT_ERROR, OrderStatus.ERROR, OrderStatus.SUCCESS):
            log_name = f"Ответ SAP"
        elif status in (OrderStatus.EDIT_MES_ERROR, OrderStatus.MES_ERROR, OrderStatus.MES_SUCCESS):
            log_name = f"Ответ MES"
        else:
            log_name = "Smi internal"
        Log.objects.create(order=instance, name=log_name, message=getattr(instance, 'log_message', None))

