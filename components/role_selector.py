import discord
from discord.ui import View, Select
from services.role_service import RoleService

class RoleActionView(View):
    def __init__(self, members: list[discord.Member], options: list[discord.SelectOption], action: str, timeout = 180):
        super().__init__(timeout = timeout)
        self.members = members
        self.action = action
        
        # 动态添加 Select 组件
        select = RoleSelector(options, placeholder = "请选择身份组...")
        select.callback = self.on_select # 绑定回调
        self.add_item(select)

    async def on_select(self, interaction: discord.Interaction):
        # 这里的 self.children[0] 就是我们添加的 RoleSelector
        select: RoleSelector = self.children[0] 
        selected_role_id = select.values[0]
        
        guild = interaction.guild
        role = guild.get_role(int(selected_role_id))
        
        if not role:
            await interaction.response.send_message("❌ 找不到该身份组", ephemeral=  True)
            return

        await interaction.response.defer(ephemeral = True)

        success, fail = await RoleService.batch_update_roles(
            interaction, 
            self.members, 
            role, 
            action = "add" if self.action == "bind" else "remove"
        )

        action_text = "绑定" if self.action == "bind" else "解绑"
        await interaction.followup.send(
            f"✅ **批量{action_text}完成！**\n"
            f"成功处理: {success} 人\n"
            f"失败/跳过: {fail} 人", 
            ephemeral = True
        )

# 假设你的 RoleSelector 是这样的
class RoleSelector(Select):
    def __init__(self, options, placeholder):
        super().__init__(placeholder = placeholder, options = options)