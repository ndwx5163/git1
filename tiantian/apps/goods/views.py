from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import View
from apps.goods.models import GoodSku, GoodType, IndexGoodBanner, IndexTypeGoodBanner, IndexPromotionBanner
from apps.order.models import OrderGood
from django.db.models import Q
from django_redis import get_redis_connection
from django.core.cache import cache
from django.core.paginator import Paginator


# 127.0.0.1:8000/goods/index/
class IndexView(View):
    def get(self, request):
        dict_content = cache.get("cache_index")
        if dict_content is None:
            # 获取css雪碧
            queryset_type_good = GoodType.objects.all()
            # 获取商品轮播图
            queryset_good_banner = IndexGoodBanner.objects.all().order_by("index")
            # 获取促销的商品
            queryset_promotion_banner = IndexPromotionBanner.objects.all().order_by("index")
            # 获取商品分类轮播图
            queryset_type_good_banner = IndexTypeGoodBanner.objects.all()
            for i in queryset_type_good:
                i.show_title = queryset_type_good_banner.filter(Q(type__exact=i) & Q(display_type=0)).order_by("index")
                i.show_image = queryset_type_good_banner.filter(Q(type__exact=i) & Q(display_type=1)).order_by("index")
            dict_content = {
                "queryset_type_good": queryset_type_good,
                "queryset_good_banner": queryset_good_banner,
                "queryset_promotion_banner": queryset_promotion_banner,
            }
            cache.set("cache_index", dict_content, 3600)
        # 获取购物车中的数量，这一部分必须要求用户登陆才能获取
        user = request.user
        count_cart = 0
        if user.is_authenticated:
            client_redis = get_redis_connection()
            count_cart = client_redis.hlen("hash_cart_user_id={}".format(user.id))
        dict_content["count_cart"] = count_cart
        return render(request, "index.html", dict_content)


class DetailView(View):

    # 127.0.0.1:8000/goods/detail/(?P<sku_id>\d+)/
    def get(self, request, sku_id):
        # 获取请求参数

        # 校验参数是否存在
        try:
            sku = GoodSku.objects.get(id__exact=sku_id)
        except GoodSku.DoesNotExist:
            return redirect(reverse("goods:index"))
        # 查询商品所有类型
        queryset_good_type = GoodType.objects.all()
        # 获取该sku的不为空的评论
        queryset_comment = OrderGood.objects.filter(sku__exact=sku).exclude(comment__exact="")
        # 查询同类型的商品，根据创建时间降序排序
        queryset_common_type_sku = GoodSku.objects.filter(type__exact=sku.type).order_by("-create_time")[:2]
        # 查询同一个SPU下面的商品
        queryset_comment_spu_sku = GoodSku.objects.filter(spu__exact=sku.spu).exclude(id__exact=sku_id)

        # 即使用户没有登陆，也允许查看那商品的详情。
        user = request.user
        count_cart = 0
        if user.is_authenticated:
            client_redis = get_redis_connection()
            count_cart = client_redis.hlen("hash_cart_user_id={}".format(user.id))
            client_redis.lrem("list_history_user_id={}".format(user.id), 0, "{}".format(sku_id))
            client_redis.rpush("list_history_user_id={}".format(user.id), "{}".format(sku_id))
            client_redis.ltrim("list_history_user_id={}".format(user.id), -5, -1)

        dict_content = {
            "sku": sku,
            "queryset_comment": queryset_comment,
            "queryset_common_type_sku": queryset_common_type_sku,
            "queryset_comment_spu_sku": queryset_comment_spu_sku,
            "count_cart": count_cart,
            "queryset_good_type": queryset_good_type
        }
        return render(request, "detail.html", dict_content)


class ListView(View):

    def get(self, request, type_id, page):
        # 获取参数
        way_sort = request.GET.get("sort")
        # 校验参数的有效性
        # 先要获取种类的信息
        queryset_good_type = GoodType.objects.all()

        try:
            obj_type = queryset_good_type.get(id__exact=type_id)
        except GoodType.DoesNotExist:
            return redirect(reverse("goods:index"))

        # 查询同类型的最新商品，根据创建时间降序排序
        queryset_common_type_sku = GoodSku.objects.filter(type__exact=obj_type).order_by("-create_time")[:2]

        # 查询该类型的所有商品。（后期可以考虑所有商品保存在cache当中）
        # 然后根据排序方式进行排序
        if way_sort == "sale":
            queryset_sku = GoodSku.objects.filter(type__exact=obj_type).order_by("sales")
        elif way_sort == "price":
            queryset_sku = GoodSku.objects.filter(type__exact=obj_type).order_by("-price")
        else:
            way_sort = "default"
            queryset_sku = GoodSku.objects.filter(type__exact=obj_type).order_by("id")

        # 对数据进行分页显示，每次执行该视图函数只传递一页的数据出去
        obj_paginator = Paginator(queryset_sku, 1)

        try:
            page = int(page)  # 当前页面页码
        except Exception:
            page = 1
        if page > obj_paginator.num_pages:
            page = 1
        obj_page = obj_paginator.page(page)  # 当前页面对象
        list_page = obj_paginator.page_range
        if obj_paginator.num_pages <= 5:
            pass
        elif page <= 3:
            list_page = list_page[:5]
        elif page >= list_page[-3]:
            list_page = list_page[-5:]
        else:
            list_page = list_page[page - 3:page + 2]

        user = request.user
        count_cart = 0
        if user.is_authenticated:
            client_redis = get_redis_connection()
            count_cart = client_redis.hlen("hash_cart_user_id={}".format(user.id))

        content = {
            "obj_page": obj_page,
            "type": obj_type,
            "queryset_common_type_sku": queryset_common_type_sku,
            "queryset_good_type": queryset_good_type,
            "count_cart": count_cart,
            "way_sort": way_sort,
            "list_page": list_page
        }

        return render(request, "list.html", content)
