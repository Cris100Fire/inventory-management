from django.urls import path

from .views import (
    ProductCreateView,
    ProductDetailView,
    ProductListView,
    ProductUpdateView,
    CategoryCreateView,
    CategoryListView,
    CategoryDetailView,
    CategoryUpdateView,
    SupplierListView,
    SupplierDetailView,
    SupplierCreateView,
    SupplierUpdateView,
)

app_name = "catalog"

urlpatterns = [
    path(
        "products/",
        ProductListView.as_view(),
        name="product_list",
    ),
    path(
        "products/create/",
        ProductCreateView.as_view(),
        name="product_create",
    ),
    path(
        "products/<int:pk>/",
        ProductDetailView.as_view(),
        name="product_detail",
    ),
    path(
        "products/<int:pk>/edit/",
        ProductUpdateView.as_view(),
        name="product_update",
    ),
    path("categories/", CategoryListView.as_view(), name="category_list"),
    path(
        "categories/create/",
        CategoryCreateView.as_view(),
        name="category_create",
    ),
    path(
        "categories/<int:pk>/",
        CategoryDetailView.as_view(),
        name="category_detail",
    ),
    path(
        "categories/<int:pk>/edit/",
        CategoryUpdateView.as_view(),
        name="category_update",
    ),
    path("suppliers/", SupplierListView.as_view(), name="supplier_list"),
    path("suppliers/create/", SupplierCreateView.as_view(), name="supplier_create"),
    path("suppliers/<int:pk>/", SupplierDetailView.as_view(), name="supplier_detail"),
    path(
        "suppliers/<int:pk>/edit/", SupplierUpdateView.as_view(), name="supplier_update"
    ),
]
