from django.contrib import admin
from django.urls import path
from django import forms
from django.shortcuts import render, redirect
from django.contrib import messages
import pandas as pd
from datetime import datetime

from smi.core.utils.etc import export_to_excel
from smi.core.utils.file_parser import xlsx_response
from smi.factory.models import Factory


def export_factories_xls(modeladmin, request, queryset):
    df_output = pd.DataFrame(
        queryset.values('plant_id', 'plantname', 'firmtext', 'created_at', 'create_by__full_name', 'updated_at',
                        'update_by__full_name').order_by('created_at'))
    df_output.columns = ['plant_id', 'plantname', 'firmtext', 'created_at', 'create_by', 'updated_at',
                         'update_by']
    excel_file = export_to_excel(df_output)
    response = xlsx_response(excel_file.read(), filename='Factories {}'.format(datetime.today().strftime('%d/%m/%Y')))
    return response


export_factories_xls.short_description = 'Export to Excel'


class CsvImportForm(forms.Form):
    csv_file = forms.FileField(label=False)


@admin.register(Factory)
class FactoryAdmin(admin.ModelAdmin):
    list_display = ['plant_id', 'id', 'plantname', 'firmtext', 'created_at', 'create_by', 'updated_at',
                    'update_by']
    list_filter = ['update_by', 'updated_at']
    readonly_fields = ('created_at', 'create_by', 'updated_at', 'update_by',)
    ordering = ('updated_at',)
    date_hierarchy = 'created_at'
    search_fields = ('plant_id', 'plantname',)
    list_per_page = 20
    change_list_template = "import.html"
    actions = [export_factories_xls]
    fieldsets = (
        (None, {
            "fields": (("plant_id",), ("plantname",), ("firmtext",), ("factory_link",), ("tex_link",))
        }),
    )

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('import-csv/', self.import_csv),
        ]
        return my_urls + urls

    def import_csv(self, request):
        if request.method == "POST":
            file_uploaded = request.FILES["csv_file"]
            if (str(file_uploaded).split('.')[-1] == 'xls') or (str(file_uploaded).split('.')[-1] == 'xlsx'):
                messages.success(request, "Your Excel file has been imported")
                df = pd.read_excel(file_uploaded)
                df.replace({pd.np.nan: None}, inplace=True)
                error_list = []
                for i, row in enumerate(df.values.tolist()):
                    try:
                        Factory.objects.update_or_create(plant_id=row[0],
                                                         defaults={'plantname': row[1], 'firmtext': row[2]})
                    except Exception as e:
                        error_list.append(f"{i + 2}. {e}")
                if error_list:
                    messages.error(request, ' '.join(error_list))
                else:
                    messages.success(request, "Success")
            else:
                messages.error(request, "File format is not correct")
            return redirect("..")
        form = CsvImportForm()
        payload = {"form": form}
        return render(
            request, "csv_form.html", payload
        )
