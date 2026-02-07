import discord

class ColorsSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Remover cor 🚫", value="none"),
            discord.SelectOption(label="˚⋆🍪｡𝐝𝐨𝐮𝐫𝐚𝐝𝐨", value="1439110891659329536"),
            discord.SelectOption(label="˚⋆💜｡𝐯𝐢𝐨𝐥𝐞𝐭𝐚", value="1439111576090050760"),
            discord.SelectOption(label="˚⋆🌪｡𝐩𝐫𝐞𝐭𝐨", value="1439113714002297014"),
            discord.SelectOption(label="˚⋆🍙｡𝐛𝐫𝐚𝐧𝐜𝐨", value="1439114721360875530"),
            discord.SelectOption(label="˚⋆☘️｡𝐜𝐢𝐚𝐧𝐨", value="1439115506048303124"),
            discord.SelectOption(label="˚⋆🍷｡𝐛𝐨𝐫𝐝𝐨", value="1439301268429340894"),
            discord.SelectOption(label="˚⋆🎀｡𝐦𝐚𝐠𝐞𝐧𝐭𝐚", value="1439301747364597925"),
            discord.SelectOption(label="˚⋆🐳｡𝐚𝐳𝐮𝐥-𝐦𝐚𝐫𝐢𝐧𝐡𝐨", value="1439302494109827284"),
        ]

        super().__init__(
            placeholder="ᯓ★ SELECIONE A COR ꒰🎨‧˚˚. ᵎᵎ ",
            options=options,
            custom_id="colors_select"
        )

    async def callback(self, interaction: discord.Interaction):
        member = interaction.user

        color_roles = [
            1439110891659329536,
            1439111576090050760,
            1439113714002297014,
            1439114721360875530,
            1439115506048303124,
            1439301268429340894,
            1439301747364597925,
            1439302494109827284,
        ]

        roles_to_remove = [
            interaction.guild.get_role(r)
            for r in color_roles
            if interaction.guild.get_role(r) in member.roles
        ]

        selected_value = self.values[0]
        if selected_value == "none":
            await member.remove_roles(*roles_to_remove)
            await interaction.response.send_message(
                "Sua cor foi removida!",
                ephemeral=True
            )
            return

        role_id = int(selected_value)
        role = interaction.guild.get_role(role_id)

        if role is None:
            await interaction.response.send_message(
                "Cargo não encontrado.",
                ephemeral=True
            )
            return

        await member.remove_roles(*roles_to_remove)
        await member.add_roles(role)

        await interaction.response.send_message(
            f"Você recebeu o cargo {role.mention}!",
            ephemeral=True
        )

class ColorsView(discord.ui.LayoutView):
    def __init__(self):
        super().__init__(timeout=None)    
    container1 = discord.ui.Container(
        discord.ui.Section(
            discord.ui.TextDisplay(content="﹕🌈 𐔌・𝐂𝐎𝐑𝐄𝐒 𝐁𝐎𝐎𝐒𝐓𝐄𝐑・꒱\n˗ˏˋ ｡𖦹 **As cores daqui são especiais**, reservadas apenas aos que fortalecem o Soul com seu impulso. No 𝐑𝐞𝐢𝐧𝐨 𝐝𝐨𝐬 𝐕𝐞𝐧𝐭𝐨𝐬, esses viajantes ganham acesso a tons raros, feitos da mesma brisa que move as nuvens mais altas. Cada reação desbloqueia uma cor única, marcando seu nome com o brilho de quem sustenta a magia do lugar. 🍓 ｡˚꩜"),
            accessory=discord.ui.Thumbnail(
                media="https://cdn.discordapp.com/attachments/1439299374302630011/1469429794818097172/Picsart_26-02-06_17-29-11-387.png?ex=6987a0a3&is=69864f23&hm=47346519a427180b092f40b6ce840429f0fd050d224c5e0d2cd3c8b2d696bd43&",
            ),
        ),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.large),
        discord.ui.TextDisplay(content="###  ╰୭ ˚𝐂𝐎𝐑𝐄𝐒... ᵎᵎ\n── .✦ <@&1439110891659329536> ⭑.ᐟ\n── .✦ <@&1439111576090050760> ⭑.ᐟ\n── .✦ <@&1439113714002297014> ⭑.ᐟ\n── .✦ <@&1439114721360875530> ⭑.ᐟ\n── .✦ <@&1439115506048303124> ⭑.ᐟ\n── .✦ <@&1439301268429340894> ⭑.ᐟ\n── .✦ <@&1439301747364597925> ⭑.ᐟ\n── .✦ <@&1439302494109827284> ⭑.ᐟ"),
        discord.ui.ActionRow(
                ColorsSelect(),
        ),
        accent_colour=discord.Colour(15742293),
    )