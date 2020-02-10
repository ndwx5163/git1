
from django.contrib import admin
from django.urls import path, include,re_path


#127.0.0.1:8000/
urlpatterns = [
    path('admin/', admin.site.urls),
    path("tinymce/",include("tinymce.urls")),
    path('search/',include('haystack.urls')),
    path("cart/", include(("apps.cart.urls","apps.cart"),namespace="cart")),#购物车模块
    path("user/", include(("apps.user.urls","apps.user"),namespace="user")),
    path("order/", include(("apps.order.urls","apps.order"),namespace="order")),
    path("goods/", include(("apps.goods.urls","apps.goods"),namespace="goods")),
]
