import discord
from utils.i18n import _

class PaymentView(discord.ui.View):
    def __init__(self, url: str, price: float):
        super().__init__()
        self.add_item(
            discord.ui.Button(
                label=_("Pay {price} USD").format(price=price),
                url=url,
                style=discord.ButtonStyle.link 
            )
        )