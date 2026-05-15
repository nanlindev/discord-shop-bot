import discord
from discord import app_commands
from errors import MissingPermissionsError
from config import ADMIN_ID

def is_owner():
    async def predicate(interaction: discord.Interaction):
        if interaction.user.id == ADMIN_ID:
            return True
        else:
            raise MissingPermissionsError()
    return app_commands.check(predicate)