import discord
from discord import app_commands
from handlers.user_handler import UserHandler
from utils.i18n import _

@app_commands.command(name='login', description=_('Register or login to your account'))
@app_commands.checks.cooldown(1, 2.0)
async def login(interaction: discord.Interaction):
    result = await UserHandler.handle_user_login(interaction.user.id, interaction.user.name)
    await interaction.response.send_message(result, ephemeral=True)

@app_commands.command(name="order_list", description=_("Check my order status"))
@app_commands.checks.cooldown(1, 2.0)
async def order_list(interaction: discord.Interaction):
    await UserHandler.handle_check_orders(interaction)

def register_user_commands(tree: app_commands.CommandTree):
    tree.add_command(login)
    tree.add_command(order_list)