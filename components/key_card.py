import discord
from discord import ui

class KeyCardView(ui.View):
    def __init__(self, key_content : str):
        super().__init__(timeout = None)
        self.key_content = key_content

def create_key_display(product_name : str, key_content : str) -> discord.Embed:
    """
    :param product_name: 商品名称
    :param key_content: 卡密内容
    :return: 返回 Embed 和 View 对象
    """
    embed = discord.Embed(
        title = "🎉 购买成功！感谢惠顾",
        description = f"您购买的商品：**{product_name}**\n\n请妥善保管您的卡密，切勿泄露给他人。",
        color=discord.Color.green() # 设置卡片左侧的边框颜色为绿色
    )
    
    # 在卡片里单独加一个字段展示卡密
    embed.add_field(
        name = "🔑 您的专属卡密", 
        value = f"```\n{key_content}\n```", 
        inline = False
    )
    
    embed.set_footer(text = "如有问题请联系管理员")
    
    # 返回 Embed 和 绑定了卡密的按钮视图
    return embed