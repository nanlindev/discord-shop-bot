#卡密表
from tortoise import fields
from tortoise.models import Model
class Card(Model):
    id         = fields.IntField(pk = True)
    # 外键关联 Product
    product    = fields.ForeignKeyField("models.Product", related_name = "cards", description = "商品id")
    card_no    = fields.CharField(max_length = 100, unique = True, description = "卡密")
    # 状态 unused:正常 used:已卖 disabled:作废/过期 locked:锁定
    status     = fields.CharField(max_length = 20, default = "unused", description = "卡密状态")
    expire_at  = fields.DatetimeField(null = True, description = "销售截止时间")
    created_at = fields.DatetimeField(auto_now_add = True, description = "创建时间")
    updated_at = fields.DatetimeField(auto_now = True, description = "更新时间")

    class Meta:
        table = "card"
        indexes = [('product_id', 'status')]