from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from smi.movement import TransferLogStatus


class ErrorMesMessages:
    INVALID_DATE = dict(
        smi_message="Неправильный формат даты для передачи. SMI принимает только формат 'гггг-мм-дд'",
        message="TransferDate format is not correct. SMI receives only 'yyyy-mm-dd' format."
    )
    INVALID_FACTORY_FROM = dict(
        smi_message="Вид поля 'Завод номер' для рабочий станции отправителя не является integer SMI не может принять. ",
        message="SenderWorkStation -> PlantNo is not integer type. SMI receives only integer in length 4 for PlantNo."
    )
    INVALID_FACTORY_TO = dict(
        smi_message='Вид поля "Завод номер" для рабочий станции получателя не является integer SMI не может принять. ',
        message="ReceiverWorkStation -> PlantNo is not integer type. SMI receives only in length 4 for PlantNo."
    )
    FACTORY_FROM = dict(
        smi_message="SenderWorkStation -> PlantNo is not defined in SMI! (Номер завода отправителя не существует "
                    "SMI !)",
        message="SenderWorkStation -> PlantNo is not defined in SMI!",
    )
    ZONE_FROM = dict(
        smi_message="SenderWorkStation -> PlantNo is not defined in SMI! (Номер рабочий станции отправителя не "
                    "существует SMI !)",
        message="SenderWorkStation -> WorkStationNo is not defined in SMI!"
    )
    FACTORY_TO = dict(
        smi_message="ReceiverWorkStation -> PlantNo is not defined in SMI! (Номер завода получателя не существует "
                    "SMI !)",
        message="ReceiverWorkStation -> PlantNo is not defined in SMI!"
    )
    ZONE_TO = dict(
        smi_message="ReceiverWorkStation -> WorkStationNo is not defined in SMI! (Номер рабочий станции "
                    "получателя  не существует SMI !)",
        message="ReceiverWorkStation -> WorkStationNo is not defined in SMI!"
    )
    CARD_FROM = dict(
        smi_message="SenderConfirmID is not defined in SMI! (ID номер бейджа отправителя не определен в SMI !)",
        message="SenderConfirmID is not defined in SMI!"
    )
    CARD_TO = dict(
        smi_message="ReceiverConfirmID is not defined in SMI! (ID номер бейджа получателя не определен в SMI!)",
        message="ReceiverConfirmID is not defined in SMI!"
    )
    ZONE_PR_MOV = dict(
        smi_message="SenderWorkStation and ReceiverWorkStation did not match in SMI! (Номер рабочий станции "
                    "отправителя и номер рабочий станции получателя не совпадают в SMI !)",
        message="SenderWorkStation and ReceiverWorkStation did not match in SMI!"
    )
    CARD_FROM_PR_MOV = dict(
        smi_message="SenderConfirmID did not match in SMI! (ID номер бейджа отправителя не совпадает в таблице "
                    "product movement.)",
        message="SenderConfirmID did not match in SMI!"
    )
    CARD_TO_PR_MOV = dict(
        smi_message="ReceiverConfirmID did not match in SMI! (ID номер бейджа получателя не совпадает в таблице "
                    "product movement !)",
        message="ReceiverConfirmID did not match in SMI!"
    )


def mes_data_checker(obj, err_msgs=None, log_obj=None, raise_exception=True):
    if err_msgs is None:
        err_msgs = dict(
            smi_message='undefined error',
            message='undefined error'
        )
    if not obj:
        smi_message = err_msgs['smi_message']
        message = err_msgs['message']
        if log_obj:
            log_obj.status = TransferLogStatus.MES_ERROR
            log_obj.message = smi_message
            log_obj.save()
        if raise_exception:
            data = {
                "ErrorMessage": message,
                "RequestStatus": False
            }
            err = ValidationError(data)
            err.status_code = 200
            raise err
        return obj, smi_message, message
    return obj, None, None
