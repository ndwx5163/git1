from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import JsonResponse
from django.views.generic import View
from utils.mixin import LoginRequiredMixin
from apps.goods.models import GoodSku
from apps.user.models import Address
from apps.order.models import OrderInfo, OrderGood
from django_redis import get_redis_connection
from datetime import datetime
from django.db import transaction


class PlaceOrderView(LoginRequiredMixin, View):

    def post(self, request):
        list_sku_id = request.POST.getlist('sku_id')
        if len(list_sku_id) == 0:
            return redirect(reverse('cart:cart'))
        str_sku_id = ','.join(list_sku_id)
        try:
            list_sku_id = [int(i) for i in list_sku_id]
            qs_obj_sku = GoodSku.objects.filter(id__in=list_sku_id)
        except Exception:
            return redirect(reverse('cart:cart'))

        user = request.user
        qs_obj_address = Address.objects.filter(user__exact=user)
        client_redis = get_redis_connection()
        list_sku_count = client_redis.hmget('hash_cart_user_id={}'.format(user.id), list_sku_id)
        list_sku_count = [int(i) for i in list_sku_count]
        total_price = 0
        tran_price = 10
        total_quantity = 0
        for i, j in zip(qs_obj_sku, list_sku_count):
            i.quantity = j
            i.total_price = j * i.price
            total_price += i.total_price
            total_quantity += j

        dict_content = {}
        dict_content["qs_obj_sku"] = qs_obj_sku
        dict_content["total_price"] = total_price
        dict_content["total_quantity"] = total_quantity
        dict_content["tran_price"] = tran_price
        dict_content["qs_obj_address"] = qs_obj_address
        dict_content["total_sum"] = total_price + tran_price
        dict_content["str_sku_id"] = str_sku_id

        return render(request, 'place_order.html', dict_content)


class OrderCommitView(View):
    @transaction.atomic
    def post(self, request):
        user = request.user
        if not user.is_authenticated:
            return JsonResponse({'res': 0, 'errmsg': '111'})
        pay_method = request.POST.get('pay_method')
        address_id = request.POST.get('address_id')
        str_sku_id = request.POST.get('str_sku_id')
        if not all((pay_method, address_id, str_sku_id)):
            return JsonResponse({'res': 0, 'errmsg': '222'})
        if pay_method not in OrderInfo.DICT_PAY_METHOD:
            return JsonResponse({'res': 0, 'errmsg': '333'})
        try:
            obj_address = Address.objects.get(id__exact=int(address_id))
        except Exception:
            return JsonResponse({'res': 0, 'errmsg': '444'})
        try:
            list_sku_id = sorted([int(i) for i in str_sku_id.split(',')],reverse=False)
            qs_obj_sku = GoodSku.objects.filter(id__in=list_sku_id).order_by('id')
        except Exception:
            return JsonResponse({'res': 0, 'errmsg': '555'})
        tran_price = 10
        order_id = datetime.now().strftime('%Y%m%d%H%M%S') + str(user.id)
        client_redis = get_redis_connection()
        list_sku_count = client_redis.hmget('hash_cart_user_id={}'.format(user.id), list_sku_id)
        list_sku_count = [int(i) for i in list_sku_count]
        for i, j in zip(list_sku_count, qs_obj_sku):
            if i > j.stock:
                return JsonResponse({'res': 0, 'errmsg': '666'})
        total_price = 0
        total_amout = 0
        obj_savepoint=transaction.savepoint()
        try:
            obj_order = OrderInfo.objects.create(
                order_id=order_id,
                address=obj_address,
                user=user,
                pay_method=int(pay_method),
                tran_price=tran_price,
                total_price=0,
                total_amount=0
            )
            for i, j in zip(qs_obj_sku, list_sku_count):
                OrderGood.objects.create(
                    order=obj_order,
                    sku=i,
                    amount=j,
                    price=i.price * j
                )
                i.sales += j
                i.stock -= j
                i.save()
                total_price += i.price * j
                total_amout += j
            obj_order.total_price = total_price
            obj_order.total_amout = total_amout
            obj_order.save()
        except Exception:
            transaction.savepoint_rollback(obj_savepoint)
            return JsonResponse({'res': 0, 'errmsg': '666'})

        transaction.savepoint_commit(obj_savepoint)
        client_redis.hdel('hash_cart_user_id={}'.format(user.id), *list_sku_id)
        return JsonResponse({"res": 1, "msg": "success"})
