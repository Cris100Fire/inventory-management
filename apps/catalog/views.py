from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, UpdateView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin


from .forms import ProductForm, CategoryForm, SupplierForm
from .models import Product, Category, Supplier


class ProductListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Product
    template_name = "catalog/products/product_list.html"
    context_object_name = "products"
    queryset = Product.objects.select_related("category", "supplier").order_by("name")
    permission_required = "catalog.view_product"


class ProductDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Product
    template_name = "catalog/products/product_detail.html"
    context_object_name = "product"
    queryset = Product.objects.select_related("category", "supplier")
    permission_required = "catalog.view_product"


class ProductCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Product
    form_class = ProductForm
    template_name = "catalog/products/product_create.html"
    success_url = reverse_lazy("catalog:product_list")
    permission_required = "catalog.add_product"

    def form_valid(self, form):
        messages.success(
            self.request,
            f"El producto «{form.instance.name}» se creó correctamente.",
        )
        return super().form_valid(form)


class ProductUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Product
    form_class = ProductForm
    template_name = "catalog/products/product_update.html"
    success_url = reverse_lazy("catalog:product_list")
    permission_required = "catalog.change_product"

    def form_valid(self, form):
        messages.success(
            self.request,
            f"El producto «{form.instance.name}» se actualizó correctamente.",
        )
        return super().form_valid(form)


class CategoryListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Category
    template_name = "catalog/category/category_list.html"
    context_object_name = "categories"
    queryset = Category.objects.order_by("name")
    permission_required = "catalog.view_category"


class CategoryDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Category
    template_name = "catalog/category/category_detail.html"
    context_object_name = "category"
    permission_required = "catalog.view_category"


class CategoryCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Category
    form_class = CategoryForm
    template_name = "catalog/category/category_create.html"
    success_url = reverse_lazy("catalog:category_list")
    permission_required = "catalog.add_category"

    def form_valid(self, form):
        messages.success(
            self.request,
            f"La categoría «{form.instance.name}» se creó correctamente.",
        )
        return super().form_valid(form)


class CategoryUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = "catalog/category/category_update.html"
    context_object_name = "category"
    success_url = reverse_lazy("catalog:category_list")
    permission_required = "catalog.change_category"

    def form_valid(self, form):
        messages.success(
            self.request,
            f"La categoría «{form.instance.name}» se actualizó correctamente.",
        )
        return super().form_valid(form)


class SupplierListView(LoginRequiredMixin, PermissionRequiredMixin, ListView):
    model = Supplier
    template_name = "catalog/supplier/supplier_list.html"
    context_object_name = "suppliers"
    queryset = Supplier.objects.order_by("name")
    permission_required = "catalog.view_supplier"


class SupplierDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    model = Supplier
    template_name = "catalog/supplier/supplier_detail.html"
    context_object_name = "supplier"
    permission_required = "catalog.view_supplier"


class SupplierCreateView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = Supplier
    form_class = SupplierForm
    template_name = "catalog/supplier/supplier_create.html"
    success_url = reverse_lazy("catalog:supplier_list")
    permission_required = "catalog.add_supplier"

    def form_valid(self, form):
        messages.success(
            self.request,
            f"El proveedor «{form.instance.name}» se creó correctamente.",
        )
        return super().form_valid(form)


class SupplierUpdateView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Supplier
    form_class = SupplierForm
    template_name = "catalog/supplier/supplier_update.html"
    context_object_name = "supplier"
    success_url = reverse_lazy("catalog:supplier_list")
    permission_required = "catalog.change_supplier"

    def form_valid(self, form):
        messages.success(
            self.request,
            f"El proveedor «{form.instance.name}» se actualizó correctamente.",
        )
        return super().form_valid(form)
