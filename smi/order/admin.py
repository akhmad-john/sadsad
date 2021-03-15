from datetime import datetime
from django.db.models import F
import pandas as pd

from smi.core.utils.etc import export_to_excel
from smi.core.utils.file_parser import xlsx_response
from smi.order.models import Order, KonvOrderClose, NeKonvOrderClose, Log, TrashOrderClose, NeKonvOrderCloseReport, \
    OrderCheck
import json
import logging

from django.db.models import JSONField
from django.contrib import admin
from django.forms import widgets

from django.contrib.admin.filters import AllValuesFieldListFilter


class DropdownFilter(AllValuesFieldListFilter):
    template = 'admin/dropdown_filter.html'


logger = logging.getLogger(__name__)


class PrettyJSONWidget(widgets.Textarea):

    def format_value(self, value):
        try:
            value = json.dumps(json.loads(value), indent=2, sort_keys=True)
            # these lines will try to adjust size of TextArea to fit to content
            row_lengths = [len(r) for r in value.split('\n')]
            self.attrs['rows'] = min(max(len(row_lengths) + 2, 10), 30)
            self.attrs['cols'] = min(max(max(row_lengths) + 2, 40), 120)
            return value
        except Exception as e:
            logger.warning("Error while formatting JSON: {}".format(e))
            return super(PrettyJSONWidget, self).format_value(value)


@admin.register(TrashOrderClose)
class TrashOrderClose(admin.ModelAdmin):
    list_display = ['__str__', 'message', 'created_at']
    formfield_overrides = {
        JSONField: {'widget': PrettyJSONWidget}
    }
    readonly_fields = ('message', 'created_at', 'updated_at')
    list_filter = ('created_at',)
    date_hierarchy = 'created_at'

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


def export_konv_orders_xls(modeladmin, request, queryset):
    df_output = pd.DataFrame(queryset.values('id',
                                             'ipaddress',
                                             'serialnum',
                                             'p_number',
                                             'status',
                                             'message',
                                             'data',
                                             'created_at',
                                             ))
    df_output.columns = ['id',
                         'ipaddress',
                         'serialnum',
                         'panel number',
                         'status',
                         'message',
                         'data',
                         'created_at', ]
    excel_file = export_to_excel(df_output)
    response = xlsx_response(excel_file.read(),
                             filename='Konv order close {}'.format(datetime.today().strftime('%d/%m/%Y')))
    return response


export_konv_orders_xls.short_description = 'Export to Excel'


@admin.register(KonvOrderClose)
class KonvOrderClose(admin.ModelAdmin):
    list_display = ['__str__', 'ipaddress', 'p_number', 'serialnum', 'status', 'message', 'created_at', ]
    formfield_overrides = {
        JSONField: {'widget': PrettyJSONWidget}
    }
    readonly_fields = ('id', 'ipaddress', 'p_number', 'serialnum', 'message', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at', ('p_number', DropdownFilter))
    date_hierarchy = 'created_at'
    search_fields = ['id', 'serialnum', 'p_number']
    actions = [export_konv_orders_xls]

    def has_add_permission(self, request):
        return False


def export_nekonv_orders_xls(modeladmin, request, queryset):
    df_output = pd.DataFrame(queryset.values('id',
                                             'aufnr',
                                             'quantity',
                                             'status',
                                             'message',
                                             'data',
                                             'created_at',
                                             ))
    df_output.columns = ['id',
                         'aufnr',
                         'quantity',
                         'status',
                         'message',
                         'data',
                         'created_at', ]
    excel_file = export_to_excel(df_output)
    response = xlsx_response(excel_file.read(),
                             filename='Nekonv order close {}'.format(datetime.today().strftime('%d/%m/%Y')))
    return response


export_nekonv_orders_xls.short_description = 'Export to Excel'


@admin.register(NeKonvOrderClose)
class NeKonvOrderClose(admin.ModelAdmin):
    list_display = ['__str__', 'aufnr', 'quantity', 'status', 'message', 'created_at', ]
    formfield_overrides = {
        JSONField: {'widget': PrettyJSONWidget}
    }
    readonly_fields = ('id', 'aufnr', 'quantity', 'message', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at')
    date_hierarchy = 'created_at'
    search_fields = ['id', 'aufnr', 'quantity']
    actions = [export_nekonv_orders_xls]

    def has_add_permission(self, request):
        return False


class LogInline(admin.TabularInline):
    model = Log
    readonly_fields = ('name', 'message', 'created_at')
    extra = 0

    def has_delete_permission(self, request, obj=None):
        return False

    def has_add_permission(self, request, obj=None):
        return False


def export_orders_xls(modeladmin, request, queryset):
    df_output = pd.DataFrame(queryset.annotate(result=F('psmng') - F('counter')).values('id',
                                                                                        'aufnr',
                                                                                        'status',
                                                                                        'active',
                                                                                        'created_at',
                                                                                        'order_date',
                                                                                        'product__mat_id',
                                                                                        'product__mat_name',
                                                                                        'cycle',
                                                                                        'cycleunit',
                                                                                        'product__mat_type_name',
                                                                                        'product__unit',
                                                                                        'zone__zonename',
                                                                                        'zone__p_number',
                                                                                        'zone__ip_address',
                                                                                        'psmng',
                                                                                        'counter',
                                                                                        'result'
                                                                                        ))
    df_output.columns = ['Номер заказа SMI',
                         'Номер заказа SAP',
                         'Журнал',
                         'Статус',
                         'Дата создания',
                         'Дата заказа',
                         'Код материала',
                         'Наименование материала',
                         'Время цикла',
                         'Eдиница цикла',
                         "Вид материала",
                         'Ед.изм',
                         'Участок',
                         'Номер панели',
                         'IP адрес',
                         'План количество',
                         'Факт количество',
                         'Разница П/Ф']
    excel_file = export_to_excel(df_output)
    response = xlsx_response(excel_file.read(), filename='Orders {}'.format(datetime.today().strftime('%d/%m/%Y')))
    return response


export_orders_xls.short_description = 'Export to Excel'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'aufnr', 'zone_detail', 'factory_detail', 'product', 'psmng', 'counter', 'status', 'cycle',
                    'cycleunit', 'active', 'order_date', 'created_at']
    list_display_links = ['id', 'aufnr']
    list_filter = ['created_at', 'active', 'status', ('factory__plantname', DropdownFilter),
                   ('create_by__full_name', DropdownFilter), ('zone__zone_id', DropdownFilter)]
    readonly_fields = ('created_at', 'create_by', 'updated_at', 'update_by',)
    ordering = ('-updated_at',)
    date_hierarchy = 'created_at'
    search_fields = ('aufnr', 'id', 'product__mat_id', 'psmng')
    inlines = [LogInline]
    actions = [export_orders_xls]

    def zone_detail(self, obj):
        if obj.zone:
            return f'{obj.zone.p_number} {obj.zone.zone_id} {obj.zone.zonename}'
        else:
            return None

    def factory_detail(self, obj):
        if obj.factory:
            return f'{obj.factory.plant_id} {obj.factory.plantname}'
        else:
            return None


def export_order_logs_xls(modeladmin, request, queryset):
    df_output = pd.DataFrame(queryset.values('order__id',
                                             'order__aufnr',
                                             'name',
                                             'message',
                                             'created_at'))
    df_output.columns = ['order smi_id',
                         'order aufnr',
                         'name',
                         'message',
                         'created_at']
    excel_file = export_to_excel(df_output)
    response = xlsx_response(excel_file.read(), filename='Order logs {}'.format(datetime.today().strftime('%d/%m/%Y')))
    return response


export_order_logs_xls.short_description = 'Export to Excel'


@admin.register(Log)
class LogAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'order_id', 'message_text', 'created_at', ]
    list_filter = ['created_at', 'name']
    list_display_links = ['id', 'name']
    readonly_fields = ('id', 'order', 'name', 'message', 'created_at',)
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    search_fields = ('name', 'message', 'order__id', 'order__aufnr')
    actions = [export_order_logs_xls]

    def has_add_permission(self, request):
        return False

    # def has_delete_permission(self, request, obj=None):
    #     return False
    def order_id(self, obj):
        return obj.order.id

    def message_text(self, obj):
        return obj.message


@admin.register(NeKonvOrderCloseReport)
class NeKonvOrderCloseReportAdmin(admin.ModelAdmin):
    list_display = ['id', 'order_aufnr', 'product', 'quantity', 'zone', 'created_at', ]
    list_filter = ['created_at', 'zone', ]
    list_display_links = ['id', 'order_aufnr']
    readonly_fields = ['id', 'order', 'product', 'quantity', 'zone', 'created_at', 'updated_at', ]
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'

    def has_add_permission(self, request):
        return False

    def order_aufnr(self, obj):
        return obj.order.aufnr


@admin.register(OrderCheck)
class OrderCheckAdmin(admin.ModelAdmin):
    list_display = ['id', 'factory', 'product', 'status', 'active', 'created_at', 'create_by']
    list_filter = ['created_at', 'active', 'status']
    list_display_links = ['id', 'factory']
    readonly_fields = ['id', 'factory', 'product', 'status', 'active', 'created_at', 'updated_at', 'message',
                       'sap_message', 'create_by', 'update_by']
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    search_fields = ('message',)

    def has_add_permission(self, request):
        return False
