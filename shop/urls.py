from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("register/", views.register, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("seller/", views.seller_dashboard, name="seller_dashboard"),
    path("products/<int:product_id>/", views.product_detail, name="product_detail"),
    path("search/", views.search, name="search"),
    path("assistant/", views.assistant, name="assistant"),
]
