

class MovementLogStatus:
    SUCCESS = 'Success'
    SAP_ERROR = 'SapError'
    MES_ERROR = 'MesError'

    CHOICES = (
        (SUCCESS, SUCCESS),
        (SAP_ERROR, SAP_ERROR),
        (MES_ERROR, MES_ERROR),
    )


class TransferLogStatus:
    STATUS = (
        ('Success', 'Success'),
        ('Created', 'Created'),
        ('SapError', 'SapError'),
        ('MesError', 'MesError'),
    )
    SUCCESS = 'Success'
    CREATED = 'Created'
    SAP_ERROR = 'SapError'
    MES_ERROR = 'MES_ERROR'

    CHOICES = (
        (SUCCESS, SUCCESS),
        (CREATED, CREATED),
        (SAP_ERROR, SAP_ERROR),
        (MES_ERROR, MES_ERROR),
    )
