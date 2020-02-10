from django.shortcuts import render
from django.views.generic import View
from django.http import JsonResponse
from apps.goods.models import GoodSku
from django_redis import get_redis_connection
from utils.mixin import LoginRequiredMixin


# config set stop-writes-on-bgsave-error no
# http://127.0.0.1:8000/cart/cart/
class CartView(LoginRequiredMixin, View):
    @staticmethod
    def iter_cart(dict_cart):
        list_sku = []
        for i, j in dict_cart.items():
            obj_sku = GoodSku.objects.get(id__exact=int(i))
            obj_sku.quantity = int(j)  # 数量
            obj_sku.total = obj_sku.price * int(j)  # 小记
            list_sku.append(obj_sku)
        return list_sku

    def get(self, request):
        user = request.user
        client_redis = get_redis_connection()
        dict_cart = client_redis.hgetall("hash_cart_user_id={}".format(user.id))
        dict_content = {}
        dict_content["list_sku"] = CartView.iter_cart(dict_cart)
        dict_content["total_quantity"] = sum(i.quantity for i in dict_content["list_sku"])
        dict_content["total_price"] = sum(i.total for i in dict_content["list_sku"])
        return render(request, "cart.html", dict_content)


# config set stop-writes-on-bgsave-error no
# http://127.0.0.1:8000/cart/add/
class CartAddtionView(View):
    def post(self, request):
        # 获取请求参数
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({"res": 0, "errmsg": "用户没有登陆。"})
        sku_id = request.POST.get("sku_id")
        sku_count = request.POST.get("sku_count")
        # 校验参数的有效性
        if not all((sku_id, sku_count)):
            return JsonResponse({"res": 0, "errmsg": "不完整的数据。"})
        try:
            sku_count = int(sku_count)
        except Exception:
            return JsonResponse({"res": 0, "errmsg": "商品数量错误。"})
        # 检查sku是否存在
        try:
            obj_sku = GoodSku.objects.get(id__exact=sku_id)
        except GoodSku.DoesNotExist:
            return JsonResponse({"res": 0, "errmsg": "不存在该商品。"})
        # 业务逻辑
        client_redis = get_redis_connection()
        # 查看购物车中有没有这个键，或者直接
        r = client_redis.hget("hash_cart_user_id={}".format(user.id), str(sku_id))
        if r is not None:
            total_count = sku_count + int(r)
        else:
            total_count = sku_count
        if obj_sku.stock < total_count:
            return JsonResponse({"res": 0, "errmsg": "商品库存量不足。"})
        client_redis.hset("hash_cart_user_id={}".format(user.id), sku_id, total_count)
        cart_count = client_redis.hlen("hash_cart_user_id={}".format(user.id))
        return JsonResponse({"res": 1, "msg": "添加成功。", "cart_count": cart_count})


# config set stop-writes-on-bgsave-error no
# http://127.0.0.1:8000/cart/update/
class CartUpdateView(View):
    def post(self, request):
        """来自购物车页面修改sku的数量的ajax，请求体当中只有sku_id,sku_count"""
        # 获取请求参数
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({"res": 0, "errmsg": "not login"})
        sku_id = request.POST.get("sku_id")
        sku_count = request.POST.get("sku_count")
        # 参数校验
        if not all((sku_id, sku_count)):
            return JsonResponse({"res": 0, "errmsg": ""})
        try:
            obj_sku = GoodSku.objects.get(id__exact=sku_id)
        except Exception:
            return JsonResponse({"res": 0, "errmsg": ""})
        try:
            sku_count = int(sku_count)
        except Exception:
            return JsonResponse({"res": 0, "errmsg": ""})
        if sku_count > obj_sku.stock:
            return JsonResponse({"res": 0, "errmsg": ""})
        client_redis = get_redis_connection()
        client_redis.hset("hash_cart_user_id={}".format(user.id), sku_id, sku_count)
        list_count = client_redis.hvals("hash_cart_user_id={}".format(user.id))
        total_count = sum(int(i) for i in list_count)
        return JsonResponse({"res": 1, "msg": 'success!', 'total_count': total_count})


# http://127.0.0.1:8000/cart/delete/
class CartDeleteView(View):
    def post(self, request):
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({"res": 0, "errmsg": ''})
        sku_id = request.POST.get("sku_id")
        try:
            obj_sku = GoodSku.objects.get(id__exact=sku_id)
        except Exception:
            return JsonResponse({"res": 0, "errmsg": ''})
        client_redis = get_redis_connection()
        client_redis.hdel("hash_cart_user_id={}".format(user.id), obj_sku.id)
        list_count = client_redis.hvals("hash_cart_user_id={}".format(user.id))
        total_count = sum(int(i) for i in list_count)
        return JsonResponse({"res": 1, "msg": "success", 'total_count': total_count})
