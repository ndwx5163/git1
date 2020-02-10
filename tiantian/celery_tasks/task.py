from django.core.mail import send_mail
from tiantian import settings
from celery import Celery
from apps.goods.models import GoodType, IndexGoodBanner, IndexTypeGoodBanner, IndexPromotionBanner
from django.db.models import Q
from django.template import loader
import os

# import django
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tiantian.settings')
# django.setup()


# 创建一个Celery的实例对象，broker当中书写一个redis的IP地址和端口号/以及采用哪一个数据库
app = Celery("celery_tasks.task", broker="redis://127.0.0.1:6379/1")


# 定义一个发送邮件的函数，并且使用一个装饰器
@app.task
def async_send_mail(username, token, list_receiver):
    '''发送激活邮件'''
    subject = "邮箱标题"  # 这个不能带有换行符
    message = "这里是邮箱的内容。"
    from_email = settings.EMAIL_FROM
    list_receiver = list_receiver
    html_message = '''<h1>{0}，欢迎来到天天生鲜！</h1><p>请点击下方链接完成激活</p><p><a href="http://127.0.0.1:8000/user/active/{1}/">http://127.0.0.1:8000/user/active/{1}/</a></p>'''.format(
        username, token)
    send_mail(subject, message, from_email, list_receiver, html_message=html_message)


@app.task
def async_write_index():
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
        "queryset_promotion_banner": queryset_promotion_banner
    }
    temp = loader.get_template("static_index.html")
    str_html = temp.render(dict_content)
    file_path = os.path.join(settings.BASE_DIR, 'static/html/static_index.html')
    with open(file_path, 'w', encoding="U8") as file:
        file.write(str_html)
