#订单表
import datetime as dt
import random
from tortoise import fields
from tortoise.models import Model

class Order(Model):
    id = fields.IntField(pk = True)
    order_no = fields.CharField(max_length = 50, unique = True, description = "订单号")
    # 外键关联 User 和 Product
    user            = fields.ForeignKeyField("models.User", related_name = "orders", description = "用户id")
    product         = fields.ForeignKeyField("models.Product", related_name = "orders", description = "商品id")
    discord_id      = fields.CharField(max_length = 50, description = "discord_id")
    total_amount    = fields.FloatField(null = True, description = "订单总金额")
    # 订单状态 pending:待支付 paid:已支付/已发货 cancelled:已取消 failed:失败
    status = fields.CharField(max_length = 20, null = True, description = "订单状态") 
    payment_payload = fields.TextField(null = True, description = "支付原始数据,json")
    created_at      = fields.DatetimeField(auto_now_add = True, description = "创建时间")
    updated_at      = fields.DatetimeField(auto_now = True, description = "更新时间")

    class Meta:
        table = "order"
        indexes = [("user_id",)]

    def __init__(self, user, product, **kwargs):
        order_no = self._generate_order_no()
        total_amount           = product.price
        kwargs['user_id']      = user.id
        kwargs['discord_id']   = user.discord_id
        kwargs['product_id']   = product.id
        kwargs['total_amount'] = total_amount
        kwargs['status']       = "pending"
        kwargs['order_no']     = order_no
        super().__init__(**kwargs)

    def _generate_order_no(self):
        return f"ORD{dt.datetime.now(dt.timezone.utc).strftime('%Y%m%d%H%M%S')}{random.randint(1000, 9999)}"
    
    def is_paid(self):
        return self.status == 'paid'

    def is_created_today(self):
        return self.created_at.date() == dt.datetime.now(dt.timezone.utc).date()

    def is_valid_revenue(self):
        return self.is_created_today()
    
    @classmethod
    async def get_today_report_data(cls):
        # 获取今天的开始时间 (UTC)
        now = dt.datetime.now(dt.timezone.utc)
        start_of_day = now.replace(hour = 0, minute = 0, second = 0, microsecond = 0)

        # 查询今天的订单，并预加载关联的 User 和 Product 信息
        orders = await cls.filter(created_at__gte = start_of_day).prefetch_related('user', 'product')
        
        # 计算总营收
        total_revenue = sum(float(order.total_amount) for order in orders)
        
        return orders, total_revenue

    def get_status_label(self):
        """充血模型：返回带Emoji的状态文本"""
        labels = {
            'pending': '⏳ 待支付',
            'paid': '✅ 已支付',
            'failed': '❌ 支付失败',
            'refunded': '💸 已退款'
        }
        return labels.get(self.status, '❓ 未知状态')