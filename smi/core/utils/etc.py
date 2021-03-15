import io
import re
import pandas as pd


def get_or_none(class_, **kwargs):
    try:
        return class_.objects.get(**kwargs)
    except class_.DoesNotExist:
        pass
    except class_.MultipleObjectsReturned:
        return []
    return None


def serializer_error_msg(errors):
    return [{k: str(v[0])} for k, v in errors.items()]


def camel_to_snake(name):
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()


def export_to_excel(df, col_size=None, sheet_name=None):
    if col_size is None:
        col_size = 25
    if sheet_name is None:
        sheet_name = "Sheet 1"

    excel_file = io.BytesIO()
    xlwriter = pd.ExcelWriter(excel_file, engine='xlsxwriter', options={'remove_timezone': True})
    df.to_excel(xlwriter, sheet_name, index=False)
    worksheet = xlwriter.sheets[sheet_name]
    worksheet.set_column('A:Z', col_size)
    xlwriter.save()
    excel_file.seek(0)
    return excel_file
