from django.db import models


class BaseModel(models.Model):
    '''模型抽象基类'''
    create_time = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")
    update_time = models.DateTimeField(auto_now=True, verbose_name="更新时间")
    is_delete = models.BooleanField(default=False, verbose_name="是否逻辑删除 ")

    class Meta:
        '''BaseModel是一个抽象基类'''
        abstract = True #如果不写的话作为抽象基类被迁移文件的时候回报错



