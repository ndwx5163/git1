from haystack import indexes
from apps.goods.models import GoodSku  # 我们要搜索的是这个模型类当中的数据。


# 指定某些类的某些字段建立索引
# 索引类的命名格式：模型类名+Index
class GoodSkuIndex(indexes.SearchIndex, indexes.Indexable):
    # 这是一个索引的字段，参数use_template 是指定根据表中的那些字段建立索引文件
    text = indexes.CharField(document=True, use_template=True)

    def get_model(self):
        """返回你的模型类"""
        return GoodSku

    # 建立索引的数据：该方法返回那些数据，我就对那些数据建立索引。
    def index_quertset(self, using=None):
        return self.get_model().objects.all()
