from django.contrib import admin
from django.urls import path
from django import forms
from django.shortcuts import render, redirect
from django.contrib import messages

from datetime import datetime
from django.contrib.postgres.aggregates.general import ArrayAgg
import pandas as pd

from smi.core.utils.etc import export_to_excel
from smi.core.utils.file_parser import xlsx_response

from smi.factory.models import Factory
from smi.movement.models import IdCard, ProductMovement, MovementLog, TransferLog, LogMaterial, ProductMovementFile, \
    IdCardFile
from smi.zone.models import Zone

from django.contrib.admin.filters import AllValuesFieldListFilter


class DropdownFilter(AllValuesFieldListFilter):
    template = 'admin/dropdown_filter.html'


def export_product_movements_xls(modeladmin, request, queryset):
    df_output = pd.DataFrame(queryset.values('zone_from__factory__plant_id',
                                             'zone_from__factory__plantname',
                                             'zone_from__zone_id',
                                             'zone_from__zonename',
                                             'zone_from__p_number',
                                             'zone_from__ip_address',
                                             'zone_to__factory__plant_id',
                                             'zone_to__factory__plantname',
                                             'zone_to__zone_id',
                                             'zone_to__zonename',
                                             'zone_to__p_number',
                                             'zone_to__ip_address',
                                             'card_om__card_number',
                                             'card_om__name',
                                             'card_pm__card_number',
                                             'card_pm__name',
                                             ))
    df_output.columns = ['Номер завода',
                         'Наименование завода',
                         'Номер зона выдачи',
                         'Название зона выдачи',
                         'Номер панели',
                         'IP-адрес зона выдачи',
                         'Номер завода приемки',
                         'Наименование завода приемки',
                         'Номер зона приемки',
                         'Название зона приемки',
                         "Номер панели приемки",
                         'IP-адрес зона приемки',
                         'Номер бейджика выдачи',
                         'Владелец бейджика',
                         'Номер бейджика приемки',
                         'Владелец бейджика']
    excel_file = export_to_excel(df_output)
    response = xlsx_response(excel_file.read(),
                             filename='product-movements {}'.format(datetime.today().strftime('%d/%m/%Y')))
    return response


export_product_movements_xls.short_description = 'Export to Excel'


def export_idcards_xls(modeladmin, request, queryset):
    df_output = pd.DataFrame(queryset.values('factory__plant_id', 'factory__plantname', 'card_number', 'name'))
    df_output.columns = ['Завод номер', 'Наименование завода', '№ бейджика', 'ФИО']
    excel_file = export_to_excel(df_output)
    response = xlsx_response(excel_file.read(), filename='idcards {}'.format(datetime.today().strftime('%d/%m/%Y')))
    return response


export_idcards_xls.short_description = 'Export to Excel'


def export_movement_logs_xls(modeladmin, request, queryset):
    df_output = pd.DataFrame(queryset.values('factory', 'zone', 'status', 'message', 'created_at'))
    df_output.columns = ['factory', 'zone', 'status', 'message', 'created_at']
    excel_file = export_to_excel(df_output)
    response = xlsx_response(excel_file.read(),
                             filename='Movmenet_get_products {}'.format(datetime.today().strftime('%d/%m/%Y')))
    return response


export_movement_logs_xls.short_description = 'Export to Excel'


def export_transfer_logs_xls(modeladmin, request, queryset):
    df_output = pd.DataFrame(queryset.values('factory_from',
                                             'factory_to',
                                             'zone_from',
                                             'zone_to',
                                             'postingdate',
                                             'requestdate',
                                             'card_from',
                                             'card_to',
                                             'status',
                                             'message',
                                             'created_at', ).annotate(materials=ArrayAgg('log_materials__material')))
    df_output.columns = ['factory_from',
                         'factory_to',
                         'zone_from',
                         'zone_to',
                         'postingdate',
                         'requestdate',
                         'card_from',
                         'card_to',
                         'status',
                         'message',
                         'created_at',
                         'materials']
    excel_file = export_to_excel(df_output)
    response = xlsx_response(excel_file.read(),
                             filename='Transfer_get_products {}'.format(datetime.today().strftime('%d/%m/%Y')))
    return response


export_transfer_logs_xls.short_description = 'Export to Excel'


class CsvImportForm(forms.Form):
    csv_file = forms.FileField(label=False)


@admin.register(ProductMovement)
class ProductMovementAdmin(admin.ModelAdmin):
    list_display = ['id', 'factory_from', 'zonefrom', 'zone_from_panel_number', 'factory_to', 'zoneto',
                    'zone_to_panel_number', 'card_om', 'card_pm']
    list_display_links = ['id', ]
    list_filter = [('zone_from__factory__plantname', DropdownFilter), ('zone_from__p_number', DropdownFilter),
                   ('zone_to__p_number', DropdownFilter)]
    ordering = ('created_at',)
    search_fields = ('card_om__card_number', 'card_pm__card_number', 'card_om__name', 'card_pm__name',)
    list_per_page = 50
    date_hierarchy = 'created_at'
    actions = [export_product_movements_xls]
    change_list_template = "import.html"
    fieldsets = (
        (None, {
            "fields": (("zone_from", "zone_to"),)
        }),
        (None, {
            "fields": (("card_om", "card_pm"),)
        }),
    )

    def factory_from(self, obj):
        return obj.zone_from.factory

    def factory_to(self, obj):
        return obj.zone_to.factory

    def zonefrom(self, obj):
        return f'{obj.zone_from.zone_id} - {obj.zone_from.zonename}'

    def zoneto(self, obj):
        return f'{obj.zone_to.zone_id} - {obj.zone_to.zonename}'

    def zone_to_panel_number(self, obj):
        return obj.zone_to.p_number

    def zone_from_panel_number(self, obj):
        return obj.zone_from.p_number

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
                    zone_from = None
                    zone_to = None
                    card_om = None
                    card_pm = None
                    if len(row) == 10:
                        if row[0]:
                            if Factory.objects.filter(plant_id=row[0]).exists():
                                factory_from = Factory.objects.get(plant_id=row[0])
                                if row[4]:
                                    if IdCard.objects.filter(card_number=row[4]).exists():
                                        if IdCard.objects.filter(factory=factory_from, card_number=row[4]).exists():
                                            card_om = IdCard.objects.get(factory=factory_from, card_number=row[4])
                                        else:
                                            error_list.append(
                                                {f"Error at {i + 2}": "Factory from and idcard_om did not match!"})
                                    else:
                                        error_list.append(
                                            {f"Error at [{i + 2}][E]": "card_om number is not defined in SMI!"})
                                else:
                                    error_list.append({f"Error at [{i + 2}][E]": "card_om number must not be empty!"})
                                if row[1]:
                                    if Zone.objects.filter(zone_id=row[1]).exists():
                                        if row[2]:
                                            if Zone.objects.filter(p_number=row[2]).exists():
                                                if row[3]:
                                                    if Zone.objects.filter(ip_address=row[3]).exists():
                                                        if Zone.objects.filter(factory=factory_from, zone_id=row[1],
                                                                               p_number=row[2],
                                                                               ip_address=row[3]).exists():
                                                            zone_from = Zone.objects.get(factory=factory_from,
                                                                                         zone_id=row[1],
                                                                                         p_number=row[2],
                                                                                         ip_address=row[3])
                                                        else:
                                                            error_list.append({
                                                                                  f"Error at {i + 2}": "Factory from, zone_from_zone_id, zone_from_p_number and zone_from_ip_address did not much!"})
                                                    else:
                                                        error_list.append({
                                                                              f"Error at [{i + 2}][D]": "Zone from ip address is not defined in SMI!"})
                                                else:
                                                    error_list.append({
                                                                          f"Error at [{i + 2}][D]": "Zone from ip address must not be empty"})
                                            else:
                                                error_list.append({
                                                                      f"Error at [{i + 2}][C]": "Zone from panel number is not defined in SMI!"})
                                        else:
                                            error_list.append({
                                                                  f"Error at [{i + 2}][C]": "Zone from ip panel number must not be empty!"})
                                    else:
                                        error_list.append(
                                            {f"Error at [{i + 2}][B]": "Zone from zone_id is not defined in SMI!"})
                                else:
                                    error_list.append({f"Error at [{i + 2}][B]": "Zone from zone_id must not be empty"})
                            else:
                                error_list.append({f"Error at [{i + 2}][A]": "Factory from is not defined in SMI!"})
                        else:
                            error_list.append({f"Error at [{i + 2}][A]": "Factory from must not be empty!"})

                        if row[5]:
                            if Factory.objects.filter(plant_id=row[5]).exists():
                                factory_to = Factory.objects.get(plant_id=row[5])
                                if row[9]:
                                    if IdCard.objects.filter(card_number=row[9]).exists():
                                        if IdCard.objects.filter(factory=factory_to, card_number=row[9]).exists():
                                            card_pm = IdCard.objects.get(factory=factory_to, card_number=row[9])
                                        else:
                                            error_list.append(
                                                {f"Error at {i + 2}": "Factory to and idcard pm did not match!"})
                                    else:
                                        error_list.append(
                                            {f"Error at [{i + 2}][J]": "card_pm number is not defined in SMI!"})
                                else:
                                    error_list.append({f"Error at [{i + 2}][J]": "card_pm number must not be empty!"})
                                if row[6]:
                                    if Zone.objects.filter(zone_id=row[6]).exists():
                                        if row[7]:
                                            if Zone.objects.filter(p_number=row[7]).exists():
                                                if row[8]:
                                                    if Zone.objects.filter(ip_address=row[8]).exists():
                                                        if Zone.objects.filter(factory=factory_to, zone_id=row[6],
                                                                               p_number=row[7],
                                                                               ip_address=row[8]).exists():
                                                            zone_to = Zone.objects.get(factory=factory_to,
                                                                                       zone_id=row[6], p_number=row[7],
                                                                                       ip_address=row[8])
                                                        else:
                                                            error_list.append({
                                                                                  f"Error at {i + 2}": "Factory to, zone_to_id, zone_to_p_number and zone_to_ip_address did not much!"})
                                                    else:
                                                        error_list.append({
                                                                              f"Error at [{i + 2}][I]": "Zone to ip address is not defined in SMI!"})
                                                else:
                                                    error_list.append({
                                                                          f"Error at [{i + 2}][I]": "Zone to ip address must not be empty"})
                                            else:
                                                error_list.append({
                                                                      f"Error at [{i + 2}][H]": "Zone to panel number is not defined in SMI!"})
                                        else:
                                            error_list.append({
                                                                  f"Error at [{i + 2}][H]": "Zone to ip panel number must not be empty!"})
                                    else:
                                        error_list.append(
                                            {f"Error at [{i + 2}][G]": "Zone to zone_id is not defined in SMI!"})
                                else:
                                    error_list.append({f"Error at [{i + 2}][G]": "Zone to zone_id must not be empty"})
                            else:
                                error_list.append({f"Error at [{i + 2}][F]": "Factory to is not defined in SMI!"})
                        else:
                            error_list.append({f"Error at [{i + 2}][F]": "Factory to must not be empty!"})

                        if zone_from and zone_to and card_om and card_pm:
                            try:
                                ProductMovement.objects.update_or_create(zone_from=zone_from, zone_to=zone_to,
                                                                         card_om=card_om, card_pm=card_pm)
                            except Exception as e:
                                error_list.append(f"{i}. {e}")
                    else:
                        error_list.append(f"{i}. List index is out of range")
                if error_list:
                    messages.error(request, ' '.join(map(str, error_list)))
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


@admin.register(IdCard)
class IdCardAdmin(admin.ModelAdmin):
    fields = (
        'factory',
        'card_number',
        'name'
    )
    list_display = ['id', 'card_number', 'name', 'factory_plant_id', 'factory_name']
    list_display_links = ['id', 'card_number']
    list_filter = [('factory__plantname', DropdownFilter)]
    ordering = ('-id',)
    search_fields = ('card_number', 'name', 'factory__plant_id',)
    list_per_page = 20
    actions = [export_idcards_xls]
    change_list_template = "import.html"

    def factory_plant_id(self, obj):
        return obj.factory.plant_id

    def factory_name(self, obj):
        return obj.factory.plantname

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('import-csv/', self.import_csv),
        ]
        return my_urls + urls

    def import_csv(self, request):
        if request.method == "POST":
            file_uploaded = request.FILES["csv_file"]
            parese_result = None
            if (str(file_uploaded).split('.')[-1] == 'xls') or (str(file_uploaded).split('.')[-1] == 'xlsx'):
                messages.success(request, "Your Excel file has been imported")
                df = pd.read_excel(file_uploaded)
                df.replace({pd.np.nan: None}, inplace=True)
                error_list = []
                for i, row in enumerate(df.values.tolist()):
                    if row[1]:
                        try:
                            IdCard.objects.update_or_create(factory=Factory.objects.get(plant_id=row[0]),
                                                            card_number=row[1], defaults={'name': row[2]})
                        except Exception as e:
                            error_list.append(f"{i + 2}. {e}")
                    else:
                        error_list.append(f"{i + 2}. Id card is an empty")
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


@admin.register(MovementLog)
class MovementLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'factory_detail', 'zone_detail', 'status', 'message', 'created_at']
    readonly_fields = ['id', 'factory', 'zone', 'status', 'message', 'created_at', 'updated_at']
    list_display_links = ['id', 'factory_detail']
    list_filter = ['created_at', 'status', ('zone', DropdownFilter), ('factory', DropdownFilter)]
    ordering = ('-created_at',)
    search_fields = ('id', 'factory', 'zone',)
    date_hierarchy = 'created_at'
    list_per_page = 50
    actions = [export_movement_logs_xls]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def factory_detail(self, obj):
        if obj.factory:
            if is_int(obj.factory):
                if Factory.objects.filter(plant_id=int(obj.factory)).exists():
                    return Factory.objects.get(plant_id=obj.factory)
        return obj.factory

    def zone_detail(self, obj):
        if obj.zone:
            if Zone.objects.filter(p_number=obj.zone).exists():
                zone = Zone.objects.get(p_number=obj.zone)
                return f'{zone.p_number} {zone.zone_id}  {zone.zonename}'
        return obj.zone


class LogMaterialAdmin(admin.TabularInline):
    model = LogMaterial
    readonly_fields = ['id', 'material', 'materialquan']
    list_display = ['id', 'material']
    extra = 0

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


def is_int(n):
    try:
        float_n = float(n)
        int_n = int(float_n)
    except ValueError:
        return False
    else:
        return float_n == int_n


@admin.register(TransferLog)
class TransferLogAdmin(admin.ModelAdmin):
    list_display = ['id', 'factory_from_detail', 'zone_from_detail', 'panel_from', 'card_from_detail',
                    'factory_to_detail', 'zone_to_detail', 'panel_to', 'card_to_detail', 'postingdate', 'requestdate',
                    'status', 'message', 'created_at']
    readonly_fields = ['id', 'factory_from', 'factory_to', 'zone_from', 'zone_to', 'postingdate', 'card_from',
                       'requestdate', 'card_to', 'status', 'message', 'updated_at']
    list_display_links = ['id', 'factory_from_detail']
    list_filter = ['status', 'created_at', ('factory_from', DropdownFilter), ('factory_to', DropdownFilter),
                   ('zone_from', DropdownFilter), ('zone_from', DropdownFilter)]
    ordering = ('-updated_at',)
    search_fields = ('id', 'card_from', 'card_to',)
    date_hierarchy = 'created_at'
    list_per_page = 50
    inlines = [LogMaterialAdmin]
    actions = [export_transfer_logs_xls]

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def factory_from_detail(self, obj):
        if obj.factory_from:
            if is_int(obj.factory_from):
                if Factory.objects.filter(plant_id=int(obj.factory_from)).exists():
                    return Factory.objects.get(plant_id=obj.factory_from)
        return obj.factory_from

    def factory_to_detail(self, obj):
        if obj.factory_to:
            if is_int(obj.factory_to):
                if Factory.objects.filter(plant_id=int(obj.factory_to)).exists():
                    return Factory.objects.get(plant_id=obj.factory_to)
        return obj.factory_to

    def zone_from_detail(self, obj):
        if obj.zone_from:
            if Zone.objects.filter(p_number=obj.zone_from).exists():
                zone = Zone.objects.get(p_number=obj.zone_from)
                return f'{zone.zone_id}  {zone.zonename}'
        return obj.zone_from

    def panel_from(self, obj):
        return obj.zone_from

    def zone_to_detail(self, obj):
        if obj.zone_to:
            if Zone.objects.filter(p_number=obj.zone_to).exists():
                zone = Zone.objects.get(p_number=obj.zone_to)
                return f'{zone.zone_id}  {zone.zonename}'
        return obj.zone_to

    def panel_to(self, obj):
        return obj.zone_to

    def card_from_detail(self, obj):
        if obj.card_from:
            if IdCard.objects.filter(card_number=obj.card_from).exists():
                return IdCard.objects.get(card_number=obj.card_from)
        return obj.card_from

    def card_to_detail(self, obj):
        if obj.card_to:
            if IdCard.objects.filter(card_number=obj.card_to).exists():
                return IdCard.objects.get(card_number=obj.card_to)
        return obj.card_to


admin.site.register(ProductMovementFile)
admin.site.register(IdCardFile)

