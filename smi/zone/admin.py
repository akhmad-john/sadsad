from django.contrib import admin
from django.urls import path
from django import forms
from django.shortcuts import render, redirect
from django.contrib import messages
import pandas as pd
from datetime import datetime

from smi.core.utils.etc import export_to_excel
from smi.core.utils.file_parser import xlsx_response
from smi.zone.models import Zone
from smi.factory.models import Factory
from smi.zone.utils.file_parser import zones_list_to_models


def export_zones_xls(modeladmin, request, queryset):
    df_output = pd.DataFrame(queryset.values(
        'factory__plant_id',
        'factory__plantname',
        'zone_id',
        'zonename',
        'indicator__display_name',
        'direction__display_name',
        'head_panel',
        'ip_address',
        'p_number',
        'create_by__full_name',
        'created_at'
    ))
    df_output.columns = (
        'factory__plant_id',
        'factory__plantname',
        'zone_id',
        'zonename',
        'indicator__displayname',
        'direction__displayname',
        'head_panel',
        'ip_address',
        'p_number',
        'create_by',
        'created_at'
    )
    excel_file = export_to_excel(df_output)
    response = xlsx_response(excel_file.read(), filename='Zones {}'.format(datetime.today().strftime('%d/%m/%Y')))
    return response


export_zones_xls.short_description = 'Export to Excel'


class CsvImportForm(forms.Form):
    csv_file = forms.FileField(label=False)


@admin.register(Zone)
class ZoneAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'zonename',
        'zone_id',
        'factory',
        'indicator',
        'head_panel',
        'p_number',
        'p_name',
        'ip_address',
        'direction',
        'created_at',
        'create_by',
        'final_point',
    )
    list_display_links = (
        'id',
        'zonename',
    )
    list_filter = (
        'factory',
        'direction',
        'indicator',
        'created_at',
        'final_point',
    )
    readonly_fields = (
        'created_at',
        'create_by',
        'updated_at',
        'update_by',
    )
    ordering = (
        '-created_at',
    )
    date_hierarchy = 'created_at'
    search_fields = (
        'zonename',
        'zone_id',
        'id',
        'p_number',
        'head_panel',
        'p_name'
    )
    list_per_page = 50
    actions = [export_zones_xls]
    change_list_template = "import.html"

    def factory_plant_id(self, obj):
        return obj.factory.plant_id

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('import-csv/', self.import_csv),
        ]
        return my_urls + urls

    def import_csv(self, request):
        if request.method == "POST":
            file_uploaded = request.FILES["csv_file"]
            if (str(file_uploaded).split('.')[-1] == 'xlsx') or (str(file_uploaded).split('.')[-1] == 'xls'):
                messages.success(request, "Your Excel file has been imported")
                df = pd.read_excel(file_uploaded)
                df.replace({pd.np.nan: None}, inplace=True)
                error_list = zones_list_to_models(df.values.tolist())
                for i, row in enumerate(df.values.tolist()):
                    try:
                        factory = Factory.objects.get(plant_id=row[0])
                        Zone.objects.update_or_create(factory=factory,
                                                      zone_id=row[1],
                                                      zonename=row[2],
                                                      head_panel=row[4],
                                                      p_number=row[5],
                                                      ip_address=row[6],
                                                      indicator=row[3],
                                                      direction=row[7])
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
