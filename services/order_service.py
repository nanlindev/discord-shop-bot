import json
import discord
from tortoise.transactions import in_transaction
from models.order import Order
from models.product import Product
from models.card import Card
from components.key_card import create_key_display
from loguru import logger
from typing import List
from utils.notification import notify_admin
from errors import InnerHandledError
class OrderService:
    @staticmethod
    async def handle_payment_success(session_data, client):
        user_id    = session_data.metadata.user_id
        discord_id = session_data.metadata.discord_id
        product_id = session_data.metadata.product_id
        order_id   = session_data.metadata.order_id
        payload_json = json.dumps(session_data.to_dict())
        order = await Order.get_or_none(id = order_id).prefetch_related('product')
        if not order:
            raise Exception('订单不存在')
        if order.status != 'pending':
            if order.status == 'paid':
                logger.warning(f'订单{order_id}重复回调')
                return {'status': 'success', 'message': '订单已处理'}
            raise Exception(f'订单状态异常:{order.status}')

        async with in_transaction() as conn:
            try:
                product = await Product.filter(id = product_id).using_db(conn).select_for_update().first()
                if not product or product.status != 'normal':
                    await OrderService._handle_failure(order, payload_json, '商品不存在或已下架', conn)
                if product.stock <= 0:
                    await OrderService._handle_failure(order, payload_json, '库存不足', conn)
                card = await Card.filter(product_id = product_id, status = 'unused').using_db(conn).select_for_update().first()
                if not card:
                    await OrderService._handle_failure(order, payload_json, '卡密库存不足', conn)
                card.status = 'used'
                await card.save(using_db = conn)
                product.stock -= 1
                await product.save(using_db = conn)
                order.status = 'paid'
                order.payment_payload = payload_json
                await order.save(using_db = conn)
            except Exception as e:
                raise e
            
        #先发卡后处理db事务,防止发送失败但数据库已更新
        try:
            user = await client.fetch_user(int(discord_id))
            embed = create_key_display(product.name, card.card_no)
            await user.send(embed = embed)
            logger.info(f'卡密已发送给用户:{user_id}')
        except discord.HTTPException:
            await OrderService._handle_failure(order, payload_json, f"【严重警告】订单 {order.id} 扣款成功，但发卡失败！请管理员手动将卡密 {card.card_no} 发送给 用户 {user.name}", conn)
            logger.error(f'【严重警告】订单 {order.id} 扣款成功，但发卡失败！请管理员手动将卡密 {card.card_no} 发送给 用户 {user.name}')
        except Exception as e:
            logger.error(f'卡密发送失败:{e}')
    
    @staticmethod
    async def _handle_failure(order, payload_json, reason, conn):
        order.status = 'failed'
        order.payment_payload = payload_json
        await order.save(using_db = conn)
        #todo 通知管理员
        await notify_admin(title = '❌ 自动发卡失败', content = f'用户{order.discord_id}购买{order.product.name}失败,原因{reason}')
        raise InnerHandledError()
    
    @staticmethod
    async def get_user_orders(discord_id: int, limit: int = 10) -> List[Order]:
        orders = await Order.filter(
            user__discord_id = discord_id  # 通过关联的 User 表查询
        ).prefetch_related(
            'product'  # 关键点：把关联的 Product 对象一次性查出来
        ).order_by(
            '-created_at'  # 按时间倒序
        ).limit(limit)
        
        return orders
