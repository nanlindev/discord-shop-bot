#商品表
from tortoise import fields
from tortoise.models import Model
class Product(Model):
    id          = fields.IntField(pk = True)
    name        = fields.CharField(max_length = 100, description = "商品名称")
    description = fields.TextField(null = True, description = "商品描述")
    price       = fields.DecimalField(max_digits = 10, decimal_places = 2, default = 0, description = "价格")
    stock       = fields.IntField(default = 0, description = "库存")
    # 商品模式 card:卡密,需要走库存检查 fixed:固定内容,不走库存检查
    type        = fields.CharField(max_length = 20, null = True, description = "商品模式")
    # 状态 normal:正常 disabled:下架
    status      = fields.CharField(max_length = 20, default = "normal", description = "商品状态")
    created_at  = fields.DatetimeField(auto_now_add = True, description = "上架时间")
    updated_at  = fields.DatetimeField(auto_now = True, description = "更新时间")

    class Meta:
        table = "product"
