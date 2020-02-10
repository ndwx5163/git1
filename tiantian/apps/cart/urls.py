from django.urls import path,re_path
from apps.cart.views import CartView, CartAddtionView, CartUpdateView, CartDeleteView
#127.0.0.1:8000/user/
urlpatterns = [
    path('cart/',CartView.as_view(),name="cart"),#
    path('add/',CartAddtionView.as_view(),name="add"),#
    path('update/',CartUpdateView.as_view(),name="update"),#
    path('delete/',CartDeleteView.as_view(),name="delete"),#

]