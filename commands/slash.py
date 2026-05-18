import discord
from discord import app_commands
from utils.logger_config import logger
# 引入 i18n 翻译函数
from utils.i18n import _

@app_commands.command(name='hello', description=_('Say hello to someone'))
@app_commands.checks.cooldown(1, 2.0)
async def hello(interaction: discord.Interaction, name: str):
    user_name = name or interaction.user.display_name
    
    logger.info(f'User {interaction.user} used /hello command')
    
    reply_text = _("Hello, {user_name}! 👋").format(user_name=user_name)
    await interaction.response.send_message(reply_text)
    
    logger.success('hello command executed successfully')

def register_slash_commands(tree: app_commands.CommandTree):
    tree.add_command(hello)

logger.info('✅ Slash command module (commands.slash) loaded')