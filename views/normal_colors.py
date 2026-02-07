import discord

class NormalColorsSelect(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Remover cor 🚫", value="none"),
            discord.SelectOption(label="ᯓ★🍌ˎˊ˗ 𝐚𝐦𝐚𝐫𝐞𝐥𝐨ᶜᵒʳ𖦹°‧", value="1438964720077111316"),
            discord.SelectOption(label="ᯓ★🥭ˎˊ˗ 𝐥𝐚𝐫𝐚𝐧𝐣𝐚ᶜᵒʳ𖦹°‧", value="1438971183109505235"),
            discord.SelectOption(label="ᯓ★🧊ˎˊ˗ 𝐚𝐳𝐮𝐥ᶜᵒʳ𖦹°‧", value="1438965121459425320"),
            discord.SelectOption(label="ᯓ★🌶ˎˊ˗ 𝐯𝐞𝐫𝐦𝐞𝐥𝐡𝐨ᶜᵒʳ𖦹°‧", value="1438965310932783245"),
            discord.SelectOption(label="ᯓ★🍑ˎˊ˗ 𝐫𝐨𝐬𝐚ᶜᵒʳ𖦹°‧", value="1438965654140096623"),
            discord.SelectOption(label="ᯓ★🍏ˎˊ˗ 𝐯𝐞𝐫𝐝𝐞ᶜᵒʳ𖦹°‧", value="1438965981308522586"),
        ]

        super().__init__(
            placeholder="ᯓᡣ𐭩 SELECIONE A COR ꒰🎨 ‧˚˚. ᵎᵎ ",
            options=options,
            custom_id="normal_colors_select",
        )

    async def callback(self, interaction: discord.Interaction):
        member = interaction.user

        color_roles = [
            1438964720077111316,
            1438971183109505235,
            1438965121459425320,
            1438965310932783245,
            1438965654140096623,
            1438965981308522586,
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
                ephemeral=True,
            )
            return

        role_id = int(selected_value)
        role = interaction.guild.get_role(role_id)

        if role is None:
            await interaction.response.send_message(
                "Cargo não encontrado.",
                ephemeral=True,
            )
            return

        await member.remove_roles(*roles_to_remove)
        await member.add_roles(role)

        await interaction.response.send_message(
            f"Você recebeu o cargo {role.mention}!",
            ephemeral=True,
        )


class NormalColorsView(discord.ui.LayoutView):
    def __init__(self):
        super().__init__(timeout=None)

    container1 = discord.ui.Container(
        discord.ui.Section(
            discord.ui.TextDisplay(content="### ⋆. 🍡˚࿔ 𝐂𝐎𝐑𝐄𝐒 𝐁𝐀𝐒𝐄 𝜗𝜚˚⋆\n‧₊ ᵎᵎ✮⋆˙Escolha a cor que mais combina com você e destaque seu nome no servidor! No 𝐑𝐞𝐢𝐧𝐨 𝐝𝐨𝐬 𝐕𝐞𝐧𝐭𝐨𝐬, cada reação aplica a cor escolhida ao seu nick — um toque de estilo ou seu estandarte pessoal. Reaja para receber o cargo, troque reagindo a outra cor ou remova clicando novamente. 🍍ᝰ.ᐟ"),
            accessory=discord.ui.Thumbnail(
                media="https://cdn.discordapp.com/attachments/1439299374302630011/1469496501074923601/Picsart_26-02-06_21-54-17-483.png?ex=6987dec3&is=69868d43&hm=b8e6cf9917f2d0694b19a0d97be1b963ea7f92ca0dcbe353ccf5d2336d37c290&",
            ),
        ),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.large),
        discord.ui.TextDisplay(content="⋮ ⌗𝐂𝐎𝐑𝐄𝐒... ╮\n\nʚଓ ּ ֶָ֢. <@&1438964720077111316>\nʚଓ ּ ֶָ֢. <@&1438971183109505235>\nʚଓ ּ ֶָ֢. <@&1438965121459425320>\nʚଓ ּ ֶָ֢. <@&1438965310932783245>\nʚଓ ּ ֶָ֢. <@&1438965654140096623>\nʚଓ ּ ֶָ֢. <@&1438965981308522586>"),
        discord.ui.ActionRow(
            NormalColorsSelect(),
        ),
        accent_colour=discord.Colour(15574859),
    )