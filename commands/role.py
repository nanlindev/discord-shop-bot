# commands/role.py
import discord
from discord import app_commands, SelectOption
from utils.logger_config import logger
from utils.role import is_owner
from services.role_service import RoleService
from components.role_selector import RoleActionView 
from config import ROLE_MAP 
from utils.i18n import _ 

role_group = app_commands.Group(name='role', description=_("🛠️ Role management"))

def get_options_for_action(action: str):
    """Generate options based on action"""
    options = []
    emoji = "✅" if action == "bind" else "❌"
    for label, role_id in ROLE_MAP.items():
        if role_id:
            options.append(SelectOption(label=label, value=str(role_id), emoji=emoji))
    return options

@role_group.command(name='bind', description=_("Batch bind roles"))
@is_owner()
async def bind(interaction: discord.Interaction, members_str: str):
    # 1. Parse members
    members = RoleService.parse_members(members_str, interaction.guild)
    if not members:
        await interaction.response.send_message(_("❌ No valid users found"), ephemeral=True)
        return

    # 2. Prepare options
    options = get_options_for_action("bind")
    if not options:
        await interaction.response.send_message(_("❌ System roles are not configured"), ephemeral=True)
        return

    # 3. Send message with View
    view = RoleActionView(members, options, action="bind")
    await interaction.response.send_message(
        _("👇 Please select the role to bind for {count} user(s):\n{mentions}").format(
            count=len(members), 
            mentions=", ".join([m.mention for m in members])
        ),
        view=view,
        ephemeral=True
    )

@role_group.command(name='unbind', description=_("Batch unbind roles"))
@is_owner()
async def unbind(interaction: discord.Interaction, members_str: str):
    # 1. Parse members
    members = RoleService.parse_members(members_str, interaction.guild)
    if not members:
        await interaction.response.send_message(_("❌ No valid users found"), ephemeral=True)
        return

    # 2. Prepare options
    options = get_options_for_action("unbind")
    if not options:
        await interaction.response.send_message(_("❌ System roles are not configured"), ephemeral=True)
        return

    # 3. Send message with View
    view = RoleActionView(members, options, action="unbind")
    await interaction.response.send_message(
        _("👇 Please select the role to unbind for {count} user(s):\n{mentions}").format(
            count=len(members), 
            mentions=", ".join([m.mention for m in members])
        ),
        view=view,
        ephemeral=True
    )

def register_role_commands(tree: app_commands.CommandTree):
    tree.add_command(role_group)

logger.info('✅ Role module loaded')