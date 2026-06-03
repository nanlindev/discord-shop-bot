import datetime as dt
import random
from tortoise import fields
from tortoise.models import Model
from utils.i18n import _

class Order(Model):
    id = fields.IntField(pk=True)
    order_no = fields.CharField(max_length=50, unique=True, description="Order Number")
    # Foreign keys linking to User and Product
    user = fields.ForeignKeyField("models.User", related_name="orders", description="User ID")
    product = fields.ForeignKeyField("models.Product", related_name="orders", description="Product ID")
    discord_id = fields.CharField(max_length=50, description="Discord ID")
    total_amount = fields.FloatField(null=True, description="Total Order Amount")
    # Order status codes: pending, paid, cancelled, failed
    status = fields.CharField(max_length=20, null=True, description="Order Status") 
    payment_payload = fields.TextField(null=True, description="Raw Payment Data (JSON)")
    created_at = fields.DatetimeField(auto_now_add=True, description="Created At")
    updated_at = fields.DatetimeField(auto_now=True, description="Updated At")

    class Meta:
        table = "order"
        indexes = [("user_id",)]

    def __init__(self, user, product, **kwargs):
        order_no = self._generate_order_no()
        total_amount = product.price
        kwargs['user_id'] = user.id
        kwargs['discord_id'] = user.discord_id
        kwargs['product_id'] = product.id
        kwargs['total_amount'] = total_amount
        kwargs['status'] = "pending"
        kwargs['order_no'] = order_no
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
        # Get the start time of today (UTC)
        now = dt.datetime.now(dt.timezone.utc)
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)

        # Query today's orders and prefetch related User and Product info
        orders = await cls.filter(created_at__gte=start_of_day).prefetch_related('user', 'product')
        
        # Calculate total revenue
        total_revenue = sum(float(order.total_amount) for order in orders)
        
        return orders, total_revenue

    def get_status_label(self):
        """Rich model: Returns status text with Emoji"""
        labels = {
            'pending': _("⏳ Pending Payment"),
            'paid': _("✅ Paid"),
            'failed': _("❌ Payment Failed"),
            'refunded': _("💸 Refunded")
        }
        return labels.get(self.status, _("❓ Unknown Status"))