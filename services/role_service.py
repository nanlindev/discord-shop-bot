import discord
from typing import List, Tuple
from loguru import logger

class RoleService:
    @staticmethod
    def parse_members(members_str: str, guild: discord.Guild) -> List[discord.Member]:
        """Parse user IDs from the string and return a list of Member objects"""
        import re
        # Extract numeric IDs from Discord mention format <@!123456> or <@123456>
        user_ids = re.findall(r'<@!?(\d+)>', members_str)
        members = []
        for user_id in user_ids:
            member = guild.get_member(int(user_id))
            if member:
                members.append(member)
        return members

    @staticmethod
    async def batch_update_roles(
        interaction: discord.Interaction, 
        members: List[discord.Member], 
        role: discord.Role, 
        action: str  # "add" or "remove"
    ) -> Tuple[int, int]:
        """
        Batch add or remove roles.
        Returns: (success_count, fail_count)
        """
        success_count = 0
        fail_count = 0

        for member in members:
            try:
                has_role = role in member.roles
                if action == "add":
                    if not has_role:
                        await member.add_roles(role)
                    success_count += 1
                elif action == "remove":
                    if has_role:
                        await member.remove_roles(role)
                    success_count += 1
            except discord.Forbidden:
                fail_count += 1
                # 1. 日志只改成纯英文，不加 _()，保持服务器日志纯净
                logger.warning(f"Insufficient permissions to operate on {member.name}")
            except Exception as e:
                fail_count += 1
                # 2. 日志只改成纯英文，不加 _()，方便直接复制报错信息去搜索解决方案
                logger.warning(f"Failed to operate on {member.name}: {e}")
        
        return success_count, fail_count