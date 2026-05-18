from tortoise import fields
from tortoise.models import Model

class Card(Model):
    id = fields.IntField(pk=True)
    # Foreign key linking to Product
    product = fields.ForeignKeyField(
        "models.Product", 
        related_name="cards", 
        description="Product ID"
    )
    card_no = fields.CharField(
        max_length=100, 
        unique=True, 
        description="License Key"
    )
    # Status codes: unused, used, disabled, locked
    status = fields.CharField(
        max_length=20, 
        default="unused", 
        description="Key Status"
    )
    expire_at = fields.DatetimeField(
        null=True, 
        description="Sales Deadline"
    )
    created_at = fields.DatetimeField(
        auto_now_add=True, 
        description="Created At"
    )
    updated_at = fields.DatetimeField(
        auto_now=True, 
        description="Updated At"
    )

    class Meta:
        table = "card"
        indexes = [('product_id', 'status')]