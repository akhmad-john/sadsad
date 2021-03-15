from datetime import datetime

from xlsxwriter.utility import xl_rowcol_to_cell


def check_pr_movement_file_row(row_num, err_template=None, **kwargs):
    if err_template is None:
        err_template = "{} is not defined in SMI!"
    for i, item in enumerate(kwargs.items()):
        if not item[1]:
            return {f"Error at {xl_rowcol_to_cell(row_num, i)}": err_template.format(item[0])}


def is_correct_date_form(d):
    try:
        datetime.strptime(d, "%Y-%m-%d")
        return True
    except ValueError:
        return False
