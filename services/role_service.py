import discord
from typing import List, Tuple
from loguru import logger

class RoleService:
    @staticmethod
    def parse_members(members_str: str, guild: discord.Guild) -> List[discord.Member]:
        """解析字符串中的用户ID，返回Member对象列表"""
        import re
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
        action: str # "add" or "remove"
    ) -> Tuple[int, int]:
        """
        批量添加或移除角色
        返回: (成功数, 失败数)
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
                logger.warning(f"权限不足，无法操作 {member.name}")
            except Exception as e:
                fail_count += 1
                logger.warning(f"操作 {member.name} 失败: {e}")
        
        return success_count, fail_count