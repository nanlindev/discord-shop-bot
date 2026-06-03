import discord
import asyncio
import stripe
import logging
import config
from discord.ext import commands
from handlers.messages import handle_message
from utils.logger_config import logger
from commands import slash, role, user, shop, admin
# Database initialization
from tortoise import Tortoise
from models.config import TORTOISE_ORM
# Webhook server
import uvicorn
from handlers.api import app, router as api_router
# Global listener for user interaction events
import errors
from models.user import User
from models.setting import Setting
# Internationalization
from utils.i18n import _, set_language, command_translator

# Third-party payment configuration
stripe.api_key = config.STRIPE_API_KEY
stripe.api_version = config.STRIPE_API_VERSION

# Bot instance configuration
intents = discord.Intents.default()
intents.message_content = True
intents.members = True
intents.presences = True
    
client = commands.Bot(
    command_prefix='?', 
    intents=intents, 
    proxy=config.PROXY_URL
) 

# Global parameter initialization
async def global_setting_init():
    setting = await Setting.get_or_none(key='shop_status')
    if setting and setting.value == 'on':
        config.SHOP_STATUS = True

# Global error handler for slash commands
@client.tree.error
async def on_app_command_error(interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
    user_locale = str(interaction.locale).replace('-', '_')
    if isinstance(error, errors.ShopMaintenanceError):
        await interaction.response.send_message(str(error), ephemeral=True)
    elif isinstance(error, errors.MissingPermissionsError):
        await interaction.response.send_message(str(error), ephemeral=True)
        logger.warning(f"Warning: User {interaction.user} attempted to use admin commands")
    elif isinstance(error, errors.SpamDetectedError):
        await interaction.response.send_message(str(error), ephemeral=True)
    elif isinstance(error, errors.SuspiciousTransactionError):
        await interaction.response.send_message(str(error), ephemeral=True)
        admin_user = client.get_user(config.ADMIN_ID)
        if admin_user:
            embed = discord.Embed(
                title=_("🚨 Risk Control Interception Alert", user_locale), 
                description=_("Detected suspicious economic system operation!", user_locale), 
                color=discord.Color.red()
            )
            embed.add_field(name=_("Suspect", user_locale), value=f"{interaction.user.mention} (`{interaction.user.id}`)")
            embed.add_field(name=_("Server", user_locale), value=interaction.guild.name if interaction.guild else "DM")
            embed.add_field(name=_("Interception Reason", user_locale), value=str(error))
            embed.add_field(name=_("Triggered Command", user_locale), value=f"`/{interaction.command.name}`")
            embed.set_thumbnail(url=interaction.user.avatar.url)
            embed.set_footer(text=f"{_('Time', user_locale)}: {discord.utils.format_dt(discord.utils.utcnow(), style='R')}")
            try:
                await admin_user.send(embed=embed)
            except:
                pass
    else:
        logger.error(
            f"🚨 Unknown Error | User: {interaction.user} ({interaction.user.id}) | "
            f"Server: {interaction.guild.name if interaction.guild else 'DM'} | "
            f"Command: /{interaction.command.name} | "
            f"Reason: {str(error)}",
            exc_info=True
        )
        await interaction.response.send_message(_("❌ An unknown error occurred. The incident has been logged.", user_locale), ephemeral=True)

app.include_router(api_router)

# Intercept standard library logs and redirect them to loguru
class InterceptHandler(logging.Handler):
    def emit(self, record):
        logger_opt = logger.opt(depth=6, exception=record.exc_info)
        logger_opt.log(record.levelno, record.getMessage())

logging.basicConfig(handlers=[InterceptHandler()], level=logging.DEBUG)
logging.getLogger("tortoise").setLevel(logging.DEBUG)

# Database initialization
async def init_database():
    logger.info('Initializing database connection...')
    await Tortoise.init(config=TORTOISE_ORM)
    await Tortoise.generate_schemas(safe=True)
    logger.info('Database initialization completed!')

# Start the FastAPI webhook server
async def start_fastapi():
    app.state.discord_client = client
    uvicorn_config = uvicorn.Config(app, host='0.0.0.0', port=8000, log_level="info")
    server = uvicorn.Server(uvicorn_config)
    logger.info("Starting FastAPI server...")
    await server.serve()

# Register slash commands and start the bot instance
@client.event
async def on_ready():
    set_language(config.DEFAULT_LANGUAGE)
    await global_setting_init()
    logger.info(f'Bot started successfully: {client.user}')
    try:
        slash.register_slash_commands(client.tree)
        role.register_role_commands(client.tree)
        user.register_user_commands(client.tree)
        shop.register_shop_commands(client.tree)
        admin.register_admin_commands(client.tree)
        await client.tree.set_translator(command_translator)
        synced = await client.tree.sync()
        logger.success(f'Successfully synced {len(synced)} slash commands')
    except Exception as e:
        logger.exception(f'Command sync failed: {e}')

@client.event
async def on_message(message):
    await handle_message(message)

@client.event
async def on_interaction(interaction: discord.Interaction):
    if interaction.user.bot:
        return
    
    user_locale = str(interaction.locale).replace('-', '_')
    set_language(user_locale)
    
    asyncio.create_task(User.touch_activity(str(interaction.user.id)))

async def main():
    await init_database()
    asyncio.create_task(start_fastapi())
    logger.info('Starting Discord Bot...')
    await client.start(config.DISCORD_BOT_TOKEN)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info('Received shutdown signal (Ctrl + C), cleaning up resources...')
    finally:
        try:
            asyncio.run(Tortoise.close_connections())
        except:
            pass
        logger.info('Bot exited safely')