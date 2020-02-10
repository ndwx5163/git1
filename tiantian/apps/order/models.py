from django.db import models
from db.base_model import BaseModel


class OrderInfo(BaseModel):
    DICT_PAY_METHOD = {
        '1': '货到付款',
        '2': '微信支付',
        '3': '支付宝',
        '4': '银联支付'
    }

    PAY_METHOD_CHOICES = (
        (1, '货到付款'),
        (2, '微信支付'),
        (3, '支付宝'),
        (4, '银联支付'),
    )

    ORDER_STATUS_CHOICES = (
        (1, '待支付'),
        (2, '待发货'),
        (3, '待收货'),
        (4, '待评价'),
        (5, '已完成'),
    )
    order_id = models.CharField(max_length=128, primary_key=True, verbose_name="订单编号")
    address = models.ForeignKey(to="user.Address", on_delete=models.CASCADE, verbose_name="收货地址")
    user = models.ForeignKey(to="user.User", on_delete=models.CASCADE, verbose_name="用户")
    pay_method = models.SmallIntegerField(choices=PAY_METHOD_CHOICES, default=3, verbose_name="支付方式")
    order_status = models.SmallIntegerField(choices=ORDER_STATUS_CHOICES, default=1, verbose_name="订单状态")
    tran_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="运费")
    total_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="总价格")
    total_amount = models.IntegerField(default=1, verbose_name="总数量")
    trade_number = models.CharField(default='', max_length=2, verbose_name="支付编号")

    class Meta:
        db_table = "t_order_info"
        verbose_name = "订单"
        verbose_name_plural = verbose_name


class OrderGood(BaseModel):
    order = models.ForeignKey(to="OrderInfo", on_delete=models.CASCADE, verbose_name="订单")
    sku = models.ForeignKey(to="goods.GoodSku", on_delete=models.CASCADE, verbose_name="商品SKU")
    amount = models.IntegerField(default=1, verbose_name="商品SKU数量")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="商品价格")
    comment = models.CharField(max_length=255, default="", verbose_name="评论")

    class Meta:
        db_table = "t_order_good"
        verbose_name = "订单商品"
        verbose_name_plural = verbose_name
