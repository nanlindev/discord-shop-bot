from models.order import Order
from models.user import User
from typing import Dict
import datetime as dt

class StatService:
    @staticmethod
    async def get_dashboard_stats() -> Dict:
        # Calculate the start time of the current day in UTC
        today_start = dt.datetime.now(dt.timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        potential_orders = await Order.filter(created_at__gte=today_start).prefetch_related('user', 'product')

        # 1. Initialize statistical variables
        total_revenue = 0.0
        today_sales_count = 0
        product_stats = {}  # Product sales statistics

        for order in potential_orders:
            # Only count orders that are paid and created today
            if order.is_paid() and order.is_created_today():
                total_revenue += order.total_amount
                today_sales_count += 1

                if order.product:
                    pname = order.product.name
                    product_stats[pname] = product_stats.get(pname, 0) + 1

        # Query users with activity records
        active_users = await User.filter(last_active_at__isnull=False)
        online_count = 0
        for user in active_users:
            if user.is_online():  # Call the Model method to check real-time status
                online_count += 1

        # 2. Assemble and return the dashboard data package
        return {
            "total_revenue": total_revenue,
            "today_sales": today_sales_count,
            "online_users": online_count,
            "product_breakdown": product_stats
        }
    
    @staticmethod
    async def get_order_report_package():
        """Fetch the complete order report package for today"""
        orders, total_revenue = await Order.get_today_report_data()
        return orders, total_revenue