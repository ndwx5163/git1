from django.urls import path,re_path
from apps.goods.views import IndexView,DetailView,ListView

#127.0.0.1:8000/goods/
urlpatterns = [
    path("index/",IndexView.as_view(),name="index"),
    re_path(r"detail/(\d+)/",DetailView.as_view(),name="detail"),
    re_path(r"list/(?P<type_id>.+)/(?P<page>.+)",ListView.as_view(),name="list"),# 有QS
]