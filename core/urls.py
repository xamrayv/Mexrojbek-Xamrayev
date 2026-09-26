from django.urls import path

from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("mine/", views.my_categories, name="my_categories"),
    path("mine/<slug:slug>/", views.my_products, name="my_products"),
    path("vip/", views.vip_view, name="vip"),
    path("add/", views.product_add, name="product_add"),
    path("delete/", views.delete_categories, name="delete_categories"),
    path("delete/<slug:slug>/", views.delete_products, name="delete_products"),
    path("product/<int:pk>/delete/", views.product_delete, name="product_delete"),
]