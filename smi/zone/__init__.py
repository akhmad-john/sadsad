

class ZoneIndicator:
    NO_KONV = '0'
    KONV = '1'

    NO_KONV_DESCRIPTION = 'Не конвейерная зона'
    KONV_DESCRIPTION = 'Конвейерный зона'

    CHOICES = (
        (NO_KONV, NO_KONV_DESCRIPTION),
        (KONV, KONV_DESCRIPTION),
    )


class ZoneDirection:
    MS = 'MS'
    MT = 'MT'

    MS_DESCRIPTION = 'From MES to SAP'
    MT_DESCRIPTION = 'From MES to TEX'

    CHOICES = (
        (MS, MS_DESCRIPTION),
        (MS, MT_DESCRIPTION),
    )
