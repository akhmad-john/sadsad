from django.http import HttpResponse


def xlsx_response(data, filename='report'):
    response = HttpResponse(data,
                            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response['Content-Disposition'] = f"attachment; filename={filename}.xlsx"
    return response
