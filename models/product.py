from tortoise import fields
from tortoise.models import Model

class Product(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=100, description="Product Name")
    description = fields.TextField(null=True, description="Product Description")
    price = fields.DecimalField(max_digits=10, decimal_places=2, default=0, description="Price")
    stock = fields.IntField(default=0, description="Stock Quantity")
    # Product modes: 'card' requires stock check, 'fixed' does not
    type = fields.CharField(max_length=20, null=True, description="Product Mode")
    # Status codes: 'normal' for active, 'disabled' for delisted
    status = fields.CharField(max_length=20, default="normal", description="Product Status")
    created_at = fields.DatetimeField(auto_now_add=True, description="Listing Time")
    updated_at = fields.DatetimeField(auto_now=True, description="Updated At")

    class Meta:
        table = "product"