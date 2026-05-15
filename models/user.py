#用户表
import datetime as dt
from tortoise import fields
from tortoise.models import Model
class User(Model):
    id             = fields.IntField(pk = True, description = "用户id")
    discord_id     = fields.CharField(max_length = 50, unique = True, description = "discord_id")
    username       = fields.CharField(max_length = 100, description = "用户名")
    # 角色 admin:管理员 merchant:商户 user:普通买家 banned:封禁用户
    role           = fields.CharField(max_length = 20, null = True, description = "用户角色") 
    point          = fields.IntField(default = 0, description = "积分") 
    # 是否封禁 None:未处理 0:否 1:是
    is_banned      = fields.IntField(null = True, description = "是否封禁")
    # 是否删除 None:未处理 0:否 1:是
    is_deleted     = fields.IntField(null = True, description = "是否删除")  
    created_at     = fields.DatetimeField(auto_now_add = True, description = "创建时间")
    updated_at     = fields.DatetimeField(auto_now = True, description = "更新时间")
    last_active_at = fields.DatetimeField(null = True, description = "上次活跃时间")

    class Meta:
        table = "user"

    async def add_point(self, point : int):
        self.point += point
        await self.save()
        return self.point
    
    def is_online(self, threshold_minutes = 10):
        if not self.last_active_at:
            return False
        return self.last_active_at + dt.timedelta(minutes = threshold_minutes) > dt.datetime.now(dt.timezone.utc)
    
    @classmethod
    async def touch_activity(cls, discord_id: str):
        await cls.filter(discord_id = str(discord_id)).update(last_active_at = dt.datetime.now(dt.timezone.utc))