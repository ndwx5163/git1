from django.contrib import admin
from apps.goods.models import GoodSku, GoodType, GoodSpu, IndexGoodBanner, IndexTypeGoodBanner, IndexPromotionBanner
from celery_tasks.task import async_write_index
from django.core.cache import cache


class BaseModelAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        async_write_index.delay()
        cache.delete("cache_index")

    def delete_model(self, request, obj):
        super().delete_model(request, obj)
        async_write_index.delay()
        cache.delete("cache_index")


class GoodTypeAdmin(BaseModelAdmin):
    list_display = ["id", "name", "image", "logo", "create_time"]


class GoodSpuAdmin(BaseModelAdmin):
    list_display = ["id", "name", "detail", "create_time"]


class IndexGoodBannerAdmin(BaseModelAdmin):
    list_display = ["id", "sku", "image", "index", "create_time"]


class IndexTypeGoodBannerAdmin(BaseModelAdmin):
    list_display = ["id", "type", "sku", "display_type", "index"]


class IndexPromotionBannerAdmin(BaseModelAdmin):
    list_display = ["id", "name", "url", "index", "image", "create_time"]


class GoodSkuAdmin(BaseModelAdmin):
    list_display = ["id", "name", "type", "spu", "price", "stock"]


admin.site.register(GoodType, GoodTypeAdmin)
admin.site.register(GoodSpu, GoodSpuAdmin)
admin.site.register(GoodSku, GoodSkuAdmin)
admin.site.register(IndexGoodBanner, IndexGoodBannerAdmin)
admin.site.register(IndexTypeGoodBanner, IndexTypeGoodBannerAdmin)
admin.site.register(IndexPromotionBanner, IndexPromotionBannerAdmin)
