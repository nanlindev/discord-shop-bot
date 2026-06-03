import discord
from typing import Dict
from utils.i18n import _

def create_dashboard_display(stats: Dict) -> discord.Embed:
    revenue = stats.get("total_revenue", 0)      
    sales   = stats.get("today_sales", 0)          
    online  = stats.get("online_users", 0)        
    products: Dict[str, int] = stats.get("product_breakdown", {}) 

    top_products = sorted(products.items(), key=lambda x: x[1], reverse=True)
    
    product_template = _("{name}: **{count}**")
    
    product_text = "\n".join([product_template.format(name=name, count=count) for name, count in top_products])
    
    if not product_text:
        product_text = _("No sales data available")

    embed = discord.Embed(
        # 4. 标题和描述全部换成英文并用 _() 包裹
        title=_("📊 Real-time Operations Dashboard"),
        description=_("Data updated: <t:{timestamp}:R>").format(timestamp=int(discord.utils.utcnow().timestamp())), 
        color=discord.Color.green() 
    )

    embed.add_field(
        # 5. 字段名称换成英文并包裹 _()
        name=_("💰 Today's Revenue (USD)"),
        value=f"```css\n{revenue}```",
        inline=True
    )
    embed.add_field(
        name=_("🛒 Today's Orders"),
        value=f"```css\n{sales}```",
        inline=True
    )
    embed.add_field(
        name=_("🟢 Online Users"),
        value=f"```css\n{online}```",
        inline=True
    )

    # 6. 商品详情标题换成英文并包裹 _()
    embed.add_field(
        name=_("🔥 Top Selling Products (Top 5)"),
        value=product_text,
        inline=False 
    )

    # 7. 底部信息保持英文即可，通常不需要翻译
    embed.set_footer(text="Powered by StatService")

    return embed