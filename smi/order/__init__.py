default_app_config = 'smi.order.apps.OrderConfig'


class OrderStatus:
    CREATED = 'Created'
    SEND = 'Send'
    SUCCESS = 'Success'
    ERROR = 'Error'
    EDIT_ERROR = 'EditError'
    EDIT_MES_ERROR = 'EditMesError'
    MES_SEND = 'MesSend'
    MES_SUCCESS = 'MesSuccess'
    MES_ERROR = 'MesError'
    SMI_ERROR = 'SmiError'
    SAP_ERROR = 'SapError'

    CHOICES = (
        (CREATED, 'Заказ создан в SMI'),
        (SEND, 'Заказ отправлен в SAP'),
        (SUCCESS, 'Заказ успешно был создан SAP'),
        (ERROR, 'Заказ не создан SAP (Ошибка)'),
        (EDIT_ERROR, 'EditError'),
        (EDIT_MES_ERROR, 'EditMesError'),
        (MES_SEND, 'Заказ отправлен в MES'),
        (MES_SUCCESS, 'Заказ успешно был создан MES'),
        (MES_ERROR, 'Заказ не создан MES (Ошибка)'),
        (SMI_ERROR, 'SmiError'),
        (SAP_ERROR, 'SapError'),
    )

    RELOAD_AVAILABLE_STATUSES = (
        ERROR,
        EDIT_ERROR,
        MES_ERROR,
        EDIT_MES_ERROR,
    )


class OrderCheckStatus:
    SUCCESS = 'Success'
    ERROR = 'Error'

    CHOICES = (
        (SUCCESS, SUCCESS),
        (ERROR, ERROR),
    )


class NoKonvOrderCloseStatus:
    SUCCESS = 'Success'
    MES_ERROR = 'MesError'
    ERROR = 'Error'
    SMI_ERROR = 'SmiError'

    CHOICES = (
        (SUCCESS, SUCCESS),
        (MES_ERROR, MES_ERROR),
        (ERROR, ERROR),
        (SMI_ERROR, SMI_ERROR),
    )


class KonvOrderCloseStatus:
    SUCCESS = 'Success'
    MES_ERROR = 'MesError'
    ERROR = 'Error'
    SMI_ERROR = 'SmiError'
    TEX_ERROR = 'TexError'

    CHOICES = (
        (SUCCESS, SUCCESS),
        (MES_ERROR, MES_ERROR),
        (ERROR, ERROR),
        (SMI_ERROR, SMI_ERROR),
        (TEX_ERROR, TEX_ERROR),
    )
