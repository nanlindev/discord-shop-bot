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
from utils.i18n import _

class OrderService:
    @staticmethod
    async def handle_payment_success(session_data, client):
        user_id = session_data.metadata.user_id
        discord_id = session_data.metadata.discord_id
        product_id = session_data.metadata.product_id
        order_id = session_data.metadata.order_id
        payload_json = json.dumps(session_data.to_dict())
        
        order = await Order.get_or_none(id=order_id).prefetch_related('product')
        if not order:
            raise Exception('Order does not exist')
        if order.status != 'pending':
            if order.status == 'paid':
                logger.warning(f'Order {order_id} duplicate callback')
                return {'status': 'success', 'message': 'Order already processed'}
            raise Exception(f'Order status abnormal: {order.status}')

        async with in_transaction() as conn:
            try:
                product = await Product.filter(id=product_id).using_db(conn).select_for_update().first()
                if not product or product.status != 'normal':
                    await OrderService._handle_failure(order, payload_json, 'Product does not exist or has been delisted', conn)
                if product.stock <= 0:
                    await OrderService._handle_failure(order, payload_json, 'Insufficient stock', conn)
                
                card = await Card.filter(product_id=product_id, status='unused').using_db(conn).select_for_update().first()
                if not card:
                    await OrderService._handle_failure(order, payload_json, 'License key stock insufficient', conn)
                
                card.status = 'used'
                await card.save(using_db=conn)
                product.stock -= 1
                await product.save(using_db=conn)
                order.status = 'paid'
                order.payment_payload = payload_json
                await order.save(using_db=conn)
            except Exception as e:
                raise e
            
        try:
            user = await client.fetch_user(int(discord_id))
            embed = create_key_display(product.name, card.card_no)
            await user.send(embed=embed)
            logger.info(f'License key sent to user: {user_id}')
        except discord.HTTPException:
            admin_alert_template = _("【CRITICAL WARNING】Order {order_id} charged successfully, but license key delivery failed! Please manually send key {card_no} to user {username}")
            alert_msg = admin_alert_template.format(
                order_id=order.id, 
                card_no=card.card_no, 
                username=user.name
            )
            await OrderService._handle_failure(order, payload_json, alert_msg, conn)
            logger.error(alert_msg)
        except Exception as e:
            logger.error(f'License key delivery failed: {e}')
    
    @staticmethod
    async def _handle_failure(order, payload_json, reason, conn):
        order.status = 'failed'
        order.payment_payload = payload_json
        await order.save(using_db=conn)
        admin_title = _("❌ Automatic Key Delivery Failed")
        admin_content_template = _("User {discord_id} failed to purchase {product_name}. Reason: {reason}")
        admin_content = admin_content_template.format(
            discord_id=order.discord_id, 
            product_name=order.product.name, 
            reason=reason
        )
        await notify_admin(title=admin_title, content=admin_content)
        raise InnerHandledError()
    
    @staticmethod
    async def get_user_orders(discord_id: int, limit: int = 10) -> List[Order]:
        orders = await Order.filter(
            user__discord_id=discord_id  # Query through the associated User table
        ).prefetch_related(
            'product'  # Key point: Fetch associated Product objects in one go
        ).order_by(
            '-created_at'  # Sort by time in descending order
        ).limit(limit)
        
        return orders