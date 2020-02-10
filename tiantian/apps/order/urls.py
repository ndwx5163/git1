from django.urls import path
from apps.order.views import PlaceOrderView, OrderCommitView

urlpatterns = [
    path('place/',PlaceOrderView.as_view(),name='place'),
    path('commit/',OrderCommitView.as_view(),name='commit'),
]