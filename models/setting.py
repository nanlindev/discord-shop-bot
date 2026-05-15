#卡密表
from tortoise import fields
from tortoise.models import Model
class Setting(Model):
    key   = fields.CharField(max_length = 20, pk = True)
    value = fields.TextField()

    class Meta:
        table = "setting"
