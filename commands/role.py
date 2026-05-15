# commands/role.py
import discord
from discord import app_commands, SelectOption
from utils.logger_config import logger
from utils.role import is_owner
from services.role_service import RoleService
from components.role_selector import RoleActionView 
from config import ROLE_MAP 

role_group = app_commands.Group(name = 'role', description = '🛠️ 身份组管理')

def get_options_for_action(action: str):
    """根据动作生成选项"""
    options = []
    emoji = "✅" if action == "bind" else "❌"
    for label, role_id in ROLE_MAP.items():
        if role_id:
            options.append(SelectOption(label = label, value = str(role_id), emoji = emoji))
    return options

@role_group.command(name = 'bind', description = '批量绑定身份组')
@is_owner()
async def bind(interaction: discord.Interaction, members_str: str):
    # 1. 解析成员
    members = RoleService.parse_members(members_str, interaction.guild)
    if not members:
        await interaction.response.send_message("❌ 未找到有效用户", ephemeral = True)
        return

    # 2. 准备选项
    options = get_options_for_action("bind")
    if not options:
        await interaction.response.send_message("❌ 系统未配置身份组", ephemeral = True)
        return

    # 3. 发送带有 View 的消息
    view = RoleActionView(members, options, action = "bind")
    await interaction.response.send_message(
        f"👇 请为 {len(members)} 位用户选择要绑定的身份组：\n" + ", ".join([m.mention for m in members]),
        view = view,
        ephemeral = True
    )

@role_group.command(name='unbind', description='批量解绑身份组')
@is_owner()
async def unbind(interaction: discord.Interaction, members_str: str):
    # 1. 解析成员
    members = RoleService.parse_members(members_str, interaction.guild)
    if not members:
        await interaction.response.send_message("❌ 未找到有效用户", ephemeral = True)
        return

    # 2. 准备选项
    options = get_options_for_action("unbind")
    if not options:
        await interaction.response.send_message("❌ 系统未配置身份组", ephemeral = True)
        return

    # 3. 发送带有 View 的消息
    view = RoleActionView(members, options, action="unbind")
    await interaction.response.send_message(
        f"👇 请为 {len(members)} 位用户选择要解绑的身份组：\n" + ", ".join([m.mention for m in members]),
        view=view,
        ephemeral=True
    )

def register_role_commands(tree: app_commands.CommandTree):
    tree.add_command(role_group)

logger.info('✅ 角色组模块已加载')