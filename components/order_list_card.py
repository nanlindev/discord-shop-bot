import discord
from models.order import Order

class OrderListCard:
    @staticmethod
    def create_order_list_display(orders: list[Order]) -> discord.Embed:
        """生成订单列表的 Embed"""
        if not orders:
            # 如果没有订单的兜底显示
            embed = discord.Embed(
                title="📦 我的订单",
                description="你还没有任何订单记录哦，快去商店看看吧！",
                color=discord.Color.greyple()
            )
            return embed

        embed = discord.Embed(
            title="📦 我的订单记录",
            color=discord.Color.blue()
        )

        for order in orders:
            status_label = order.get_status_label()
            product_name = order.product.name if order.product else "未知商品"
            
            time_str = order.created_at.strftime("%Y-%m-%d %H:%M")
            
            embed.add_field(
                name=f"🆔 订单号: `{order.order_no}`",
                value=(f"{product_name} - **{order.total_amount}** - {time_str} - {status_label}"),
                inline=False # 设为 False 让每个订单占一整行，清晰易读
            )

        embed.set_footer(text="仅显示最近 10 笔订单")
        return embed