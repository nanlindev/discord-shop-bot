import discord
# 定义商城维护错误
class ShopMaintenanceError(discord.app_commands.AppCommandError):
    def __init__(self):
        super().__init__("🛑 系统维护中，请稍后再试！")

# 定义权限不足错误
class MissingPermissionsError(discord.app_commands.AppCommandError):
    def __init__(self):
        super().__init__("🚫 你没有权限执行此命令！")

#冷却时间/刷屏检测
class SpamDetectedError(discord.app_commands.AppCommandError):
    def __init__(self, retry_after: float):
        super().__init__(f"⚠️ 操作太频繁了！请休息 {retry_after:.1f} 秒后再试。")

#可疑交易/经济异常
class SuspiciousTransactionError(discord.app_commands.AppCommandError):
    def __init__(self, reason: str):
        super().__init__(f"⚠️ 交易被拦截：{reason}")