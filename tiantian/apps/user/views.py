from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from apps.user.models import User, Address
import re
from django.urls import reverse
from django.views.generic import View
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
from tiantian import settings
from utils.mixin import LoginRequiredMixin
from celery_tasks.task import async_send_mail
from apps.goods.models import GoodSku
from apps.order.models import OrderInfo, OrderGood
from django_redis import get_redis_connection
from django.core.paginator import Paginator


# 127.0.0.1:8000/user/register/
class RegisterView(View):
    '''注册'''

    def get(self, request):
        return render(request, "register.html")

    def post(self, request):
        # 获取注册用的用户名，密码，邮箱，二次输入密码
        username = request.POST.get("user_name", "")
        password = request.POST.get("pwd", "")
        password_repeated = request.POST.get("cpwd", "")
        email = request.POST.get("email", "")
        allow = request.POST.get("allow", "")
        # 进行检查
        if allow != "on":
            return render(request, "register.html", {"errmsg": "没有同意用户协议"})
        # 验证输入的注册信息均不为空
        if not all((username, password, password_repeated, email)):
            # 如果数据有一个不完整,all()都会返回False
            return render(request, "register.html", {"errmsg": "注册信息不完整"})
        # 如果两次密码不相等
        if password != password_repeated:
            return render(request, "register.html", {"errmsg": "密码不一致"})
        # 验证邮箱的格式正确，使用正则表达式。
        if re.match(r"^[a-z0-9][\w.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$", email) is None:
            return render(request, "register.html", {"errmsg": "邮箱格式不正确"})
        # 检验用户名是否已经存在？
        try:
            user = User.objects.get(username__exact=username)
        except User.DoesNotExist:
            user = None
        if user is not None:
            return render(request, "register.html", {"errmsg": "用户名已存在"})
        # 检查无误之后，进行注册
        user = User.objects.create_user(username, email=email, password=password)
        user.is_active = 0
        user.save()

        # 设置用户ID的参数的密文。
        serializer = Serializer(settings.SECRET_KEY, 3600)
        data = {"user_id": user.id}
        token = serializer.dumps(data).decode("utf_8")
        list_recipient = [email]
        async_send_mail.delay(username, token, list_recipient)

        return redirect(reverse("goods:index"))


# 127.0.0.1:8000/user/active/
class ActiveView(View):
    """激活账户"""

    def get(self, request, token):
        try:
            # 实例化一个一模一样的对象
            serializer = Serializer(settings.SECRET_KEY, 3600)
            data = serializer.loads(token)
            user_id = data.get("user_id")
            # 找到这一个用户，并且激活
            user = User.objects.get(id__exact=user_id)
            user.is_active = 1
            user.save()

            return render(request, "login.html")

        except SignatureExpired:
            return redirect(reverse("user:register"))


# 127.0.0.1:8000/user/login/
class LoginView(View):
    def get(self, request):
        username = request.COOKIES.get('username', '')
        checked = request.COOKIES.get('checked', '')  # 如果有这个键而且不是空的字符串

        return render(request, "login.html", {"username": username, "checked": checked})

    def post(self, request):
        """login handle"""
        # 获取请求参数
        username = request.POST.get("username", "")
        password = request.POST.get("pwd", "")
        remember = request.POST.get("remember", "")
        # 参数校验
        # 检查是否为空
        if not all((username, password)):
            return render(request, "login.html", {"errmsg": "登录信息不完整"})
        user = authenticate(username=username, password=password)
        if user is not None:
            # the password verified for the user
            if user.is_active:
                print("User is valid,active and authenticated")
                # 将用户ID保存在session当中，保持会话
                login(request, user)  # 用于记录用户的登陆状态？？？？？？？？？？
                # 创建一个HttpResposne对象
                next = request.GET.get("next", reverse("goods:index"))
                response = redirect(next)
                if remember == "on":
                    # 需要记住用户名
                    response.set_cookie(key="username", value=username, max_age=7 * 86400)
                    response.set_cookie(key="checked", value='checked', max_age=7 * 86400)
                else:
                    response.delete_cookie(key="username")
                    response.delete_cookie(key="checked")
                return response
            else:
                print("The password is valid,but the account has been disabled!!")
                serializer = Serializer(settings.SECRET_KEY, 3600)
                token = serializer.dumps({"user_id": user.id}).decode("U8")
                async_send_mail.delay(username, token, [user.email])
                return render(request, "login.html", {"errmsg": "用户没有激活，请注意接受邮箱中的激活邮件！！"})
        else:
            print("The user name and password were incorrect!!")
            return render(request, "login.html", {"errmsg": "用户名密码错误！！"})


class LogoutView(View):
    """"""

    def get(self, request):
        # 这个会删除用户的的session信息。
        logout(request)
        return redirect(reverse("goods:index"))


# 127.0.0.1:8000/user/info/
class UserInfoView(LoginRequiredMixin, View):
    """用户个人信息"""

    def get(self, request):
        '''获取用户的用户名，电话号码，收货地址，浏览历史sku的名字，单价，单位'''
        user = request.user
        address = Address.objects.get_default_address(user)
        client_redis = get_redis_connection()
        list_sku_id = client_redis.lrange("list_history_user_id={}".format(user.id), -5, -1)[::-1]
        qs_history_sku = GoodSku.objects.filter(id__in=list_sku_id)  # 只进行一次范围查询
        list_history_sku = [qs_history_sku.get(id__exact=i) for i in list_sku_id]

        # 这个user不需要传递，因为是在request当中，所以传递request的时候就已经传递过去了。
        return render(request, "user_center_info.html",
                      {"page": "info", "address": address, "list_history_sku": list_history_sku})


# 127.0.0.1:8000/user/order/
class UserOrderView(LoginRequiredMixin, View):
    """用户个人订单"""

    def get(self, request):
        page_num = request.GET.get('page_num')
        user = request.user
        qs_obj_order = OrderInfo.objects.filter(user__exact=user).order_by('-order_id')
        for i in qs_obj_order:
            i.qs_obj_sku = OrderGood.objects.filter(order__exact=i).order_by('id')
            i.total_sum = i.tran_price + i.total_price
        try:
            page_num = int(page_num)
        except Exception:
            page_num = 1
        obj_paginator = Paginator(qs_obj_order, 2)
        obj_page = obj_paginator.page(page_num)
        list_page_num = obj_paginator.page_range
        if obj_paginator.num_pages <= 5:
            pass
        elif page_num <= 3:
            list_page_num = list_page_num[:5]
        elif page_num >= list_page_num[-3]:
            list_page_num = list_page_num[-5:]
        else:
            list_page_num = list_page_num[page_num - 3:page_num + 2]

        return render(request, "user_center_order.html",
                      {"page": "order", "obj_page": obj_page, "list_page_num": list_page_num})


# 127.0.0.1:8000/user/site/
class UserSiteView(LoginRequiredMixin, View):
    """用户地址"""

    def get(self, request):
        user = request.user
        # default_address = Address.objects.get_default_address(user)
        qs_obj_address = Address.objects.all()
        return render(request, "user_center_site.html", {"page": "site", "qs_obj_address": qs_obj_address})

    def post(self, request):
        """增加一个收货地址"""
        receiver = request.POST.get("receiver")
        phone = request.POST.get("phone")
        zip_code = request.POST.get("zip_code")  # 非必须
        address = request.POST.get("address")
        # 校验数据的完整性
        if not all((receiver, phone, address)):
            return render(request, "user_center_site.html", {"errmsg": "地址信息不完整"})
        # 校验手机号的有效性
        if re.match(r"^1[3-9]\d{9}$", phone) is None:
            return render(request, "user_center_site.html", {"errmsg": "地址信息不完整"})
        # 创建一个收货地址，如果用户已经存在默认收货地址，则新地址不作为默认地址，否则作为默认收货地址。
        user = request.user
        default_address = Address.objects.get_default_address(user)
        # 条件表达式
        is_default = True if default_address is None else False
        # 创建一个新地址对象
        Address.objects.create(user=user, receiver=receiver, phone=phone, zip_code=zip_code, address=address,
                               is_default=is_default)

        return redirect(reverse("user:site"))
