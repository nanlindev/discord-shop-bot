import discord
from discord import app_commands
from utils.logger_config import logger

@app_commands.command(name = 'hello', description = '打个招呼')
@app_commands.checks.cooldown(1, 2.0)
async def hello(interaction:discord.Interaction, name:str):
    user_name = name or interaction.user.display_name
    logger.info(f'用户{interaction.user}使用了/hello')
    await interaction.response.send_message(f'你好,{user_name}!👋')
    logger.success('hello指令执行完毕')

def register_slash_commands(tree : app_commands.CommandTree):
    tree.add_command(hello)

logger.info('✅ 斜杠指令模块(commands.slash)已加载')
