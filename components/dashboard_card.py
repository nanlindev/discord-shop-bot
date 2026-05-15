import discord
from typing import Dict

def create_dashboard_display(stats: Dict) -> discord.Embed:
    revenue = stats.get("total_revenue", 0)      # 今日营收
    sales   = stats.get("today_sales", 0)          # 今日订单数
    online  = stats.get("online_users", 0)        # 在线用户数
    products: Dict[str, int] = stats.get("product_breakdown", {}) # 商品销售明细

    top_products = sorted(products.items(), key = lambda x: x[1], reverse = True)
    product_text = "\n".join([f"{name}: **{count}** 单" for name, count in top_products])
    if not product_text:
        product_text = "暂无销量"

    embed = discord.Embed(
        title       = "📊 实时运营看板",
        description = f"数据更新至: <t:{int(discord.utils.utcnow().timestamp())}:R>", # 显示相对时间
        color       = discord.Color.green() # 既然是赚钱的数据，用点绿色或者金色
    )

    embed.add_field(
        name   = "💰 今日营收",
        value  = f"```css\n{revenue} 元```", # 用 css 代码块高亮数字
        inline = True
    )
    embed.add_field(
        name   = "🛒 今日订单",
        value  = f"```css\n{sales} 单```",
        inline = True
    )
    embed.add_field(
        name   = "🟢 在线用户",
        value  = f"```css\n{online} 人```",
        inline = True
    )

    # 5. 添加商品详情 (单独一行)
    embed.add_field(
        name   = "🔥 热销商品 (Top 5)",
        value  = product_text,
        inline = False # 占满整行
    )

    # 6. 设置底部信息 (可选)
    embed.set_footer(text="Powered by StatService")

    return embed