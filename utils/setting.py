import discord
import config
from discord import app_commands
from errors import ShopMaintenanceError

def shop_open():
    async def predicate(interaction: discord.Interaction):
        if config.SHOP_STATUS:
            return True
        else:
            raise ShopMaintenanceError()
    return app_commands.check(predicate)