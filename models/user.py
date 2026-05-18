import datetime as dt
from tortoise import fields
from tortoise.models import Model

class User(Model):
    id = fields.IntField(pk=True, description="User ID")
    discord_id = fields.CharField(max_length=50, unique=True, description="Discord ID")
    username = fields.CharField(max_length=100, description="Username")
    # Role codes: admin, merchant, user, banned
    role = fields.CharField(max_length=20, null=True, description="User Role") 
    point = fields.IntField(default=0, description="Points Balance") 
    # Ban status: None=unprocessed, 0=no, 1=yes
    is_banned = fields.IntField(null=True, description="Is Banned")
    # Deletion status (Soft Delete): None=unprocessed, 0=no, 1=yes
    is_deleted = fields.IntField(null=True, description="Is Deleted")  
    created_at = fields.DatetimeField(auto_now_add=True, description="Created At")
    updated_at = fields.DatetimeField(auto_now=True, description="Updated At")
    last_active_at = fields.DatetimeField(null=True, description="Last Active At")

    class Meta:
        table = "user"

    async def add_point(self, point: int):
        self.point += point
        await self.save()
        return self.point
    
    def is_online(self, threshold_minutes=10):
        if not self.last_active_at:
            return False
        return self.last_active_at + dt.timedelta(minutes=threshold_minutes) > dt.datetime.now(dt.timezone.utc)
    
    @classmethod
    async def touch_activity(cls, discord_id: str):
        await cls.filter(discord_id=str(discord_id)).update(last_active_at=dt.datetime.now(dt.timezone.utc))