from django.http import HttpResponseBadRequest
from django.views import View
from django.core.paginator import Paginator
from django.views.generic import TemplateView

from .mixins import ReportPermissionMixin

from .forms import (
    StockReportFilterForm,
    LowStockReportFilterForm,
    MovementReportFilterForm,
)

from .services.queries import (
    get_stock_report_queryset,
    get_stock_report_summary,
    get_low_stock_report_queryset,
    get_movement_report_queryset,
    get_movement_report_summary,
)

from .services.exporters import (
    export_stock_csv,
    export_stock_excel,
    export_movement_csv,
    export_movement_excel,
)


class StockReportView(ReportPermissionMixin, TemplateView):
    template_name = "reports/stock_report.html"
    permission_required = "catalog.view_product"
    raise_exception = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        form = StockReportFilterForm(self.request.GET or None)

        if form.is_valid():
            queryset = get_stock_report_queryset(form.cleaned_data)
        else:
            queryset = get_stock_report_queryset()

        summary = get_stock_report_summary(queryset)

        paginator = Paginator(queryset, 20)
        page_obj = paginator.get_page(self.request.GET.get("page"))

        query_params = self.request.GET.copy()
        query_params.pop("page", None)

        context.update(
            {
                "form": form,
                "summary": summary,
                "page_obj": page_obj,
                "products": page_obj.object_list,
                "filter_query": query_params.urlencode(),
            }
        )

        return context


class StockReportExportView(ReportPermissionMixin, View):
    permission_required = "catalog.view_product"
    raise_exception = True

    def get(self, request, *args, **kwargs):
        form = StockReportFilterForm(request.GET)

        if not form.is_valid():
            return HttpResponseBadRequest("Los filtros del reporte no son válidos.")

        queryset = get_stock_report_queryset(form.cleaned_data)

        export_format = kwargs.get("export_format")

        if export_format == "csv":
            return export_stock_csv(queryset)

        if export_format == "xlsx":
            return export_stock_excel(queryset)

        return HttpResponseBadRequest("Formato de exportación no válido.")


class LowStockReportView(ReportPermissionMixin, TemplateView):
    template_name = "reports/low_stock_report.html"
    permission_required = "catalog.view_product"
    raise_exception = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        form = LowStockReportFilterForm(self.request.GET or None)

        if form.is_valid():
            queryset = get_low_stock_report_queryset(form.cleaned_data)
        else:
            queryset = get_low_stock_report_queryset()

        summary = get_stock_report_summary(queryset)

        paginator = Paginator(queryset, 20)

        page_obj = paginator.get_page(self.request.GET.get("page"))

        query_params = self.request.GET.copy()
        query_params.pop("page", None)

        context.update(
            {
                "form": form,
                "summary": summary,
                "page_obj": page_obj,
                "products": page_obj.object_list,
                "filter_query": query_params.urlencode(),
            }
        )

        return context


class LowStockReportExportView(ReportPermissionMixin, View):
    permission_required = "catalog.view_product"
    raise_exception = True

    def get(self, request, *args, **kwargs):
        form = LowStockReportFilterForm(request.GET)

        if not form.is_valid():
            return HttpResponseBadRequest("Los filtros del reporte no son válidos.")

        queryset = get_low_stock_report_queryset(form.cleaned_data)

        export_format = kwargs.get("export_format")

        if export_format == "csv":
            return export_stock_csv(
                queryset,
                filename="reporte_stock_bajo.csv",
            )

        if export_format == "xlsx":
            return export_stock_excel(
                queryset,
                filename="reporte_stock_bajo.xlsx",
                sheet_name="Stock bajo",
            )

        return HttpResponseBadRequest("Formato de exportación no válido.")


class MovementReportView(ReportPermissionMixin, TemplateView):
    template_name = "reports/movements_report.html"
    permission_required = "inventory.view_stockmovement"
    raise_exception = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        form = MovementReportFilterForm(self.request.GET or None)

        if form.is_valid():
            queryset = get_movement_report_queryset(form.cleaned_data)
        else:
            queryset = get_movement_report_queryset()

        summary = get_movement_report_summary(queryset)

        paginator = Paginator(queryset, 20)

        page_obj = paginator.get_page(self.request.GET.get("page"))

        query_params = self.request.GET.copy()
        query_params.pop("page", None)

        context.update(
            {
                "form": form,
                "summary": summary,
                "page_obj": page_obj,
                "movements": page_obj.object_list,
                "filter_query": query_params.urlencode(),
            }
        )

        return context


class MovementReportExportView(ReportPermissionMixin, View):
    permission_required = "inventory.view_stockmovement"
    raise_exception = True

    def get(self, request, *args, **kwargs):
        export_format = kwargs.get("export_format")

        if export_format not in ("csv", "xlsx"):
            return HttpResponseBadRequest("Formato de exportación no válido.")

        form = MovementReportFilterForm(request.GET)

        if not form.is_valid():
            return HttpResponseBadRequest("Los filtros proporcionados no son válidos.")

        queryset = get_movement_report_queryset(form.cleaned_data)

        if export_format == "csv":
            return export_movement_csv(queryset)

        return export_movement_excel(queryset)
