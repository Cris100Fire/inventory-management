from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin

from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import DetailView, FormView, ListView
from django.db.models import Q

from .forms import StockMovementForm
from .models import StockMovement
from .services import register_stock_movement


class StockMovementListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = StockMovement
    template_name = "inventory/movement_list.html"
    context_object_name = "movements"
    permission_required = "inventory.view_stockmovement"
    paginate_by = 20

    queryset = StockMovement.objects.select_related(
        "product", "user", "supplier"
    ).order_by("-created_at")

    def get_queryset(self):
        queryset = super().get_queryset()

        # Busqueda por producto o usuario
        search_query = self.request.GET.get("q", "").strip()

        if search_query:
            queryset = queryset.filter(
                Q(product__name__icontains=search_query)
                | Q(user__username__icontains=search_query)
            )

        # Filtro por tipo de movimiento
        movement_type = self.request.GET.get("movement_type", "")
        valid_types = StockMovement.MovementType.values

        if movement_type in valid_types:
            queryset = queryset.filter(movement_type=movement_type)

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["movement_types"] = StockMovement.MovementType.choices
        return context


class StockMovementDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = StockMovement
    template_name = "inventory/movement_detail.html"
    context_object_name = "movement"
    permission_required = "inventory.view_stockmovement"

    queryset = StockMovement.objects.select_related("product", "user", "supplier")


class StockMovementCreateView(LoginRequiredMixin, PermissionRequiredMixin, FormView):
    form_class = StockMovementForm
    template_name = "inventory/movement_create.html"
    success_url = reverse_lazy("inventory:movement_list")
    permission_required = "inventory.add_stockmovement"

    def form_valid(self, form):
        try:
            movement = register_stock_movement(
                product_id=form.cleaned_data["product"].pk,
                movement_type=form.cleaned_data["movement_type"],
                quantity=form.cleaned_data["quantity"],
                user=self.request.user,
                supplier=form.cleaned_data["supplier"],
                notes=form.cleaned_data["notes"],
            )
        except ValidationError as error:
            form.add_error(None, error)
            return self.form_invalid(form)

        messages.success(
            self.request,
            f"Movimiento de «{movement.product.name}» " "registrado correctamente.",
        )
        return redirect(self.get_success_url())
