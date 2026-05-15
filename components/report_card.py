# 订单报表
import discord
import csv
import io
import datetime as dt

def create_order_report_view() -> discord.ui.View:
    """创建一个包含导出按钮的视图"""
    view = discord.ui.View(timeout = None)
    button = discord.ui.Button(label = "💾 导出完整 CSV", style=discord.ButtonStyle.green)
    button.custom_id = 'export_csv_btn'
    view.add_item(button)
    return view

def create_order_preview_embed(orders, total_revenue: float) -> discord.Embed:
    embed = discord.Embed(title = "📊 今日订单报表预览", color = discord.Color.blue())
    embed.add_field(name = "总营收", value = f"¥ {total_revenue}", inline = False)
    embed.add_field(name = "订单总数", value = f"{len(orders)} 单", inline = True)
    
    # 预览前 5 条订单
    description = ""
    for order in orders[:5]:
        status_emoji = "✅" if order.is_paid else "⏳"
        username = order.user.username if order.user else "未知用户"
        description += f"{status_emoji} **{username}** - {order.product.name if order.product else '已删除商品'} - ¥{order.total_amount}\n"
    
    if not description:
        description = "今日暂无订单。"
        
    embed.add_field(name = "最新订单 (前5条)", value = description, inline = False)
    embed.set_footer(text = "点击下方按钮导出完整 Excel/CSV 文件")

    return embed

def generate_order_csv(orders) -> discord.File:
    """生成 CSV 文件对象"""
    output = io.StringIO()
    writer = csv.writer(output)
    
    writer.writerow(["订单号", "用户ID", "用户名", "商品名称", "金额", "状态", "创建时间"])
    
    for order in orders:
        status_text = "已支付" if order.is_paid else "待支付"
        username = order.user.username if order.user else "未知"
        product_name = order.product.name if order.product else "已删除"
        created_at = order.created_at.strftime("%Y-%m-%d %H:%M:%S")
        
        writer.writerow([
            order.order_no,
            order.discord_id,
            username,
            product_name,
            order.total_amount,
            status_text,
            created_at
        ])
    
    byte_output = io.BytesIO(output.getvalue().encode('utf-8-sig'))
    filename = f"orders_{dt.datetime.now().strftime('%Y%m%d')}.csv"
    return discord.File(byte_output, filename = filename)

def generate_product_csv(products) -> discord.File:
    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow(["商品名称", "价格", "库存数量", "状态", "创建时间"])

    for product in products:
        status_text = "上架" if getattr(product, 'normal', True) else "下架" 
        created_at = product.created_at.strftime("%Y-%m-%d %H:%M:%S") if product.created_at else "未知"

        writer.writerow([
            product.name,
            f"{product.price}", # 价格
            product.stock,      # 库存
            status_text,
            created_at
        ])

    byte_output = io.BytesIO(output.getvalue().encode('utf-8-sig'))
    filename = f"products_{dt.datetime.now().strftime('%Y%m%d')}.csv"
    return discord.File(byte_output, filename = filename)