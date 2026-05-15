import discord

class PaymentView(discord.ui.View):
    def __init__(self, url : str, price : float):
        super().__init__()
        # 动态添加一个按钮，把 Stripe 生成的链接塞进去
        self.add_item(
            discord.ui.Button(
                label = f"支付 {price} 美元",
                url = url,
                style = discord.ButtonStyle.link # 链接样式的按钮
            )
        )