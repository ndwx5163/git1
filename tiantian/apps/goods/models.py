from django.db import models
from db.base_model import BaseModel
from tinymce.models import HTMLField


# Create your models here.
# 商品种类表格
class GoodType(BaseModel):
    name = models.CharField(max_length=20, verbose_name="商品种类名称")
    image = models.ImageField(upload_to="type", verbose_name="商品图片")
    logo = models.CharField(max_length=20, verbose_name="商品标识")

    class Meta:
        db_table = "t_good_type"
        verbose_name = "商品类型"
        verbose_name_plural = verbose_name

    def __str__(self):
        return '<class:{} id:{} name:{}>'.format(self.__class__.__name__,self.id,self.name)



class GoodSpu(BaseModel):
    name = models.CharField(max_length=20, verbose_name="SPU名称")
    detail = HTMLField(blank=True, verbose_name="SPU详情")

    class Meta:
        db_table = "t_good_spu"
        verbose_name = "商品SPU"
        verbose_name_plural = verbose_name

    def __str__(self):
        return '<class:{} id:{} name:{}>'.format(self.__class__.__name__,self.id,self.name)

class GoodSku(BaseModel):
    status_choices = (
        (0, "下线"),
        (1, "上线"),
    )
    spu = models.ForeignKey(to="GoodSpu", on_delete=models.CASCADE, verbose_name="SPU的id")
    type = models.ForeignKey(to="GoodType", on_delete=models.CASCADE, verbose_name="SPU的id")
    name = models.CharField(max_length=20, verbose_name="SKU名称")
    detail = models.CharField(max_length=255, verbose_name="SKU详情")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="SKU价格")
    unite = models.CharField(max_length=20, verbose_name="SKU单位")
    stock = models.IntegerField(default=1, verbose_name="SKU库存量")
    sales = models.IntegerField(default=0, verbose_name="SKU销量")
    image = models.ImageField(upload_to="good", verbose_name="SKU图片")
    status = models.SmallIntegerField(default=1, choices=status_choices, verbose_name="SKU状态")

    def __str__(self):
        return '<class:{} id:{} name:{}>'.format(self.__class__.__name__,self.id,self.name)

    class Meta:
        db_table = "t_good_sku"
        verbose_name = "商品SKU"
        verbose_name_plural = verbose_name


class GoodImage(BaseModel):
    '''商品SKU的外键'''
    sku = models.ForeignKey(to="GoodSku", on_delete=models.CASCADE, verbose_name="商品名称")
    image = models.ImageField(upload_to="good", verbose_name="图片路径")

    class Meta:
        db_table = 't_good_image'
        verbose_name = '商品图片'
        verbose_name_plural = verbose_name

    def __str__(self):
        return '<class:{} id:{} sku:{}>'.format(self.__class__.__name__,self.id,self.sku.name)



class IndexGoodBanner(BaseModel):
    '''首页轮播商品展示模型类'''
    sku = models.ForeignKey('GoodSku', on_delete=models.CASCADE, verbose_name='商品')
    image = models.ImageField(upload_to='banner', verbose_name='图片')
    index = models.SmallIntegerField(default=0, verbose_name='展示顺序')

    def __str__(self):
        return '<class:{} id:{} sku:{}>'.format(self.__class__.__name__,self.id,self.sku.name)


    class Meta:
        db_table = 't_index_banner'
        verbose_name = '首页轮播商品'
        verbose_name_plural = verbose_name


class IndexPromotionBanner(BaseModel):
    '''首页促销活动模型类'''
    name = models.CharField(max_length=20, verbose_name='活动名称')
    url = models.URLField(verbose_name='活动链接')
    image = models.ImageField(upload_to='banner', verbose_name='活动图片')
    index = models.SmallIntegerField(default=0, verbose_name='展示顺序')

    def __str__(self):
        return '<class:{} id:{} name:{}>'.format(self.__class__.__name__,self.id,self.name)

    class Meta:
        db_table = 't_index_promotion'
        verbose_name = "主页促销活动"
        verbose_name_plural = verbose_name


class IndexTypeGoodBanner(BaseModel):
    '''首页分类商品展示模型类'''
    DISPLAY_TYPE_CHOICES = (
        (0, "标题"),
        (1, "图片"),
    )
    type = models.ForeignKey('GoodType', models.CASCADE, verbose_name='商品类型')
    sku = models.ForeignKey('GoodSku', models.CASCADE, verbose_name='商品SKU')
    display_type = models.SmallIntegerField(default=1, choices=DISPLAY_TYPE_CHOICES, verbose_name='展示类型')
    index = models.SmallIntegerField(default=0, verbose_name='展示顺序')

    def __str__(self):
        return '<class:{} id:{} sku:{}>'.format(self.__class__.__name__,self.id,self.sku.name)


    class Meta:
        db_table = 't_index_type_good'
        verbose_name = "主页分类展示商品"
        verbose_name_plural = verbose_name
