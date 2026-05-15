import discord
import asyncio
import stripe
import logging
import config
from discord.ext import commands
from handlers.messages import handle_message
from utils.logger_config import logger
from commands import slash, role, user, shop, admin
#db
from tortoise import Tortoise
from models.config import TORTOISE_ORM
#webhook
import uvicorn
from handlers.api import app, router as api_router
#全局监听用户交互事件
import errors
from models.user import User
from models.setting import Setting

#三方支付
stripe.api_key = config.STRIPE_API_KEY
stripe.api_version = config.STRIPE_API_VERSION
#bot实例
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True
client = commands.Bot(command_prefix = '?', intents = intents, proxy = config.PROXY_URL)
#全局参数初始化
async def global_setting_init():
    setting = await Setting.get_or_none(key = 'shop_status')
    if setting.value == 'on':
        config.SHOP_STATUS = True
#全局错误处理
@client.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
    if isinstance(error, errors.ShopMaintenanceError):
        await interaction.response.send_message(str(error), ephemeral = True)
    elif isinstance(error, errors.MissingPermissionsError):
        await interaction.response.send_message(str(error), ephemeral = True)
        logger.warning(f"警告：用户 {interaction.user} 尝试使用管理员命令")
    elif isinstance(error, errors.SpamDetectedError):
        await interaction.response.send_message(str(error), ephemeral = True)
    elif isinstance(error, errors.SuspiciousTransactionError):
        await interaction.response.send_message(str(error), ephemeral = True)
        # 当捕获到这个错误时，立刻通知管理员
        admin_user = client.get_user(config.ADMIN_ID)
        if admin_user:
            # 构造报警信息
            embed = discord.Embed(
                title="🚨 风控拦截警报", 
                description=f"检测到可疑的经济系统操作！", 
                color=discord.Color.red()
            )
            embed.add_field(name = "嫌疑人", value = f"{interaction.user.mention} (`{interaction.user.id}`)")
            embed.add_field(name = "服务器", value = interaction.guild.name if interaction.guild else "私聊")
            embed.add_field(name = "拦截原因", value = str(error))
            embed.add_field(name = "触发命令", value = f"`/{interaction.command.name}`")
            embed.set_thumbnail(url = interaction.user.avatar.url)
            embed.set_footer(text = f"时间: {discord.utils.format_dt(discord.utils.utcnow(), style='R')}")
            try:
                await admin_user.send(embed = embed)
            except:
                pass # 管理员可能屏蔽了机器人私信
    else:
        logger.error(
            f"🚨 未知错误 | 用户: {interaction.user} ({interaction.user.id}) | "
            f"服务器: {interaction.guild.name if interaction.guild else '私聊'} | "
            f"命令: /{interaction.command.name}",
            exc_info=True  # <--- 这个参数会自动抓取完整的报错堆栈
        )
        await interaction.response.send_message("❌ 发生未知错误，已记录日志。", ephemeral = True)
app.include_router(api_router)

#拦截dblog(debug用)
class InterceptHandler(logging.Handler):
    def emit(self, record):
        logger_opt = logger.opt(depth = 6, exception = record.exc_info)
        logger_opt.log(record.levelno, record.getMessage())
logging.basicConfig(handlers = [InterceptHandler()], level = logging.DEBUG)
logging.getLogger("tortoise").setLevel(logging.DEBUG)
#db初始化
async def init_database():
    logger.info('正在初始化数据库链接...')
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas(safe = True)
    logger.info('数据库初始化完成!')
#webhook启动
async def start_fastapi():
    app.state.discord_client = client
    # 配置 Uvicorn Server
    config = uvicorn.Config(app, host = '0.0.0.0', port = 8000, log_level = "info")
    server = uvicorn.Server(config)
    logger.info("启动 FastAPI 服务器...")
    await server.serve()
#/指令注册,bot实例启动
@client.event
async def on_ready():
    await global_setting_init()
    logger.info(f'机器人已启动: {client.user}')
    try:
        slash.register_slash_commands(client.tree)
        role.register_role_commands(client.tree)
        user.register_user_commands(client.tree)
        shop.register_shop_commands(client.tree)
        admin.register_admin_commands(client.tree)
        synced = await client.tree.sync()
        logger.success(f'成功同步 {len(synced)} 个/指令')
    except Exception as e:
        logger.exception(f'指令同步失败: {e}')

@client.event
async def on_message(message):
    await handle_message(message)

@client.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.user.bot:
        return
    
    client.loop.create_task(User.touch_activity(str(interaction.user.id)))

async def main():
    await init_database()
    asyncio.create_task(start_fastapi())
    logger.info('正在启动 Discord Bot...')
    await client.start(config.DISCORD_BOT_TOKEN)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('收到关闭信号 (Ctrl + C)，正在清理资源...')
    finally:
        try:
            asyncio.run(Tortoise.close_connections())
        except:
            pass
        logger.info('机器人已安全退出')