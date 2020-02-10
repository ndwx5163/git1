from django.urls import path,re_path
from apps.user.views import RegisterView, ActiveView, LoginView, UserInfoView, UserOrderView, UserSiteView,LogoutView


#127.0.0.1:8000/user/
urlpatterns = [
    path('register/',RegisterView.as_view(),name="register"),#注册页面
    re_path(r'active/(?P<token>.*?)/',ActiveView.as_view(),name="active"),#邮箱激活链接

    path('login/',LoginView.as_view(),name="login"),#登录页面
    path('logout/',LogoutView.as_view(),name="logout"),#退出页面

    path('info/',UserInfoView.as_view(),name="info"),#用户信息页面
    path('order/',UserOrderView.as_view(),name="order"),#用户订单页面
    path('site/',UserSiteView.as_view(),name="site"),#用户地址页面

]