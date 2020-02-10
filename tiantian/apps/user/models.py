from django.db import models
from django.db.models import Q
from db.base_model import BaseModel
from django.contrib.auth.models import AbstractUser



class User(AbstractUser, BaseModel):
    """自定义User"""
    class Meta:
        db_table = 't_user'
        verbose_name = '用户'
        verbose_name_plural = verbose_name


class AddressManager(models.Manager):

    def get_default_address(self, user):

        # default=Address.objects.get(Q(user__id__exact=user.id)&Q(is_default=True))
        try:
            # self.model获取当前使用这个模型管理器的模型类对象，但是self本身就是模型管理器对象objects
            # default_address=self.model.objects.get(Q(user__exact=user)&Q(is_default__exact=True))
            default_address = self.get(Q(user__exact=user) & Q(is_default__exact=True))
        except Address.DoesNotExist:
            default_address = None

        return default_address


class Address(BaseModel):
    user = models.ForeignKey(to="User", on_delete=models.CASCADE, verbose_name="用户ID")
    receiver = models.CharField(max_length=20, verbose_name="收货人")
    address = models.CharField(max_length=255, verbose_name="收货地址")
    zip_code = models.CharField(max_length=6, null=True, verbose_name="邮政编码")
    phone = models.CharField(max_length=11, verbose_name="电话号码")
    is_default = models.BooleanField(default=False, verbose_name="是否默认地址")

    objects = AddressManager()

    class Meta:
        db_table = 't_address'
        verbose_name = '地址'
        verbose_name_plural = verbose_name
