import discord
from discord import ui
from utils.i18n import _

class KeyCardView(ui.View):
    def __init__(self, key_content: str):
        super().__init__(timeout=None)
        self.key_content = key_content

def create_key_display(product_name: str, key_content: str) -> discord.Embed:
    """
    :param product_name: Product name
    :param key_content: License key content
    :return: Returns Embed and View object
    """
    embed = discord.Embed(
        title=_("🎉 Purchase Successful! Thank you for your order"),
        description=_("You purchased: **{product_name}**\n\nPlease keep your license key safe and do not share it with others.").format(product_name=product_name),
        color=discord.Color.green()
    )
    
    embed.add_field(
        name=_("🔑 Your Exclusive License Key"), 
        value=f"```\n{key_content}\n```", 
        inline=False
    )
    
    embed.set_footer(text=_("If you have any questions, please contact an administrator"))
    
    return embed