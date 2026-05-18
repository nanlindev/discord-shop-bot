import discord
from discord.ui import View, Select
from services.role_service import RoleService
from utils.i18n import _

class RoleActionView(View):
    def __init__(self, members: list[discord.Member], options: list[discord.SelectOption], action: str, timeout=180):
        super().__init__(timeout=timeout)
        self.members = members
        self.action = action
        
        select = RoleSelector(options, placeholder=_("Please select a role..."))
        select.callback = self.on_select # 绑定回调
        self.add_item(select)

    async def on_select(self, interaction: discord.Interaction):
        select: RoleSelector = self.children[0] 
        selected_role_id = select.values[0]
        
        guild = interaction.guild
        role = guild.get_role(int(selected_role_id))
        
        if not role:
            await interaction.response.send_message(_("❌ Role not found"), ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)

        success, fail = await RoleService.batch_update_roles(
            interaction, 
            self.members, 
            role, 
            action="add" if self.action == "bind" else "remove"
        )

        action_text = _("Bind") if self.action == "bind" else _("Unbind")
        result_template = _("✅ **Batch {action} completed!**\nSuccessfully processed: {success} users\nFailed/Skipped: {fail} users")
        
        await interaction.followup.send(
            result_template.format(action=action_text, success=success, fail=fail), 
            ephemeral=True
        )

class RoleSelector(Select):
    def __init__(self, options, placeholder):
        super().__init__(placeholder=placeholder, options=options)