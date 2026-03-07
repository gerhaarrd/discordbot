import discord
import database

SHOP_ITEMS = [
    ("Remover cor 🚫", "none", 0),
    ("˚⋆🍪｡𝐝𝐨𝐮𝐫𝐚𝐝𝐨", "1439110891659329536", 6),
    ("˚⋆💜｡𝐯𝐢𝐨𝐥𝐞𝐭𝐚", "1439111576090050760", 6),
    ("˚⋆🌪｡𝐩𝐫𝐞𝐭𝐨", "1439113714002297014", 7),
    ("˚⋆🍙｡𝐛𝐫𝐚𝐧𝐜𝐨", "1439114721360875530", 7),
    ("˚⋆☘️｡𝐜𝐢𝐚𝐧𝐨", "1439115506048303124", 8),
    ("˚⋆🍷｡𝐛𝐨𝐫𝐝𝐨", "1439301268429340894", 8),
    ("˚⋆🎀｡𝐦𝐚𝐠𝐞𝐧𝐭𝐚", "1439301747364597925", 9),
    ("˚⋆🐳｡𝐚𝐳𝐮𝐥-𝐦𝐚𝐫𝐢𝐧𝐡𝐨", "1439302494109827284", 10),
]

COLOR_ROLE_IDS = [
    1439110891659329536,
    1439111576090050760,
    1439113714002297014,
    1439114721360875530,
    1439115506048303124,
    1439301268429340894,
    1439301747364597925,
    1439302494109827284,
]

PRICE_BY_ROLE_ID = {
    int(value): price for _, value, price in SHOP_ITEMS if value != "none"
}


class ColorShopSelect(discord.ui.Select):
    def __init__(self):
        options = []
        for label, value, price in SHOP_ITEMS:
            description = "Sem custo" if value == "none" else f"Custo: {price} moedas"
            options.append(discord.SelectOption(label=label, value=value, description=description))

        super().__init__(
            placeholder="ᯓ★ COMPRAR COR GRADIENTE ꒰🛍️‧˚.ᵎᵎ",
            options=options,
            custom_id="color_shop_select",
        )

    async def callback(self, interaction: discord.Interaction):
        member = interaction.user
        guild = interaction.guild
        if not isinstance(member, discord.Member) or guild is None:
            await interaction.response.send_message("Não consegui processar sua compra.", ephemeral=True)
            return

        selected_value = self.values[0]

        roles_to_remove = [role for role in (guild.get_role(rid) for rid in COLOR_ROLE_IDS) if role and role in member.roles]

        if selected_value == "none":
            if roles_to_remove:
                await member.remove_roles(*roles_to_remove, reason="Loja de cores: remover cor")
            await interaction.response.send_message("Sua cor foi removida.", ephemeral=True)
            return

        role_id = int(selected_value)
        role = guild.get_role(role_id)
        if role is None:
            await interaction.response.send_message("Cargo de cor não encontrado.", ephemeral=True)
            return

        price = PRICE_BY_ROLE_ID.get(role_id, 0)
        balance = database.get_voice_currency_balance(str(member.id))
        if balance < price:
            await interaction.response.send_message(
                f"Saldo insuficiente. Você tem {balance} moeda(s) e precisa de {price}.",
                ephemeral=True,
            )
            return

        if not database.spend_voice_currency(str(member.id), price):
            await interaction.response.send_message("Não foi possível concluir a compra. Tente novamente.", ephemeral=True)
            return

        if roles_to_remove:
            await member.remove_roles(*roles_to_remove, reason="Loja de cores: troca de cor")
        await member.add_roles(role, reason="Loja de cores: compra")

        new_balance = database.get_voice_currency_balance(str(member.id))
        await interaction.response.send_message(
            f"Compra concluída: {role.mention}. Saldo atual: {new_balance} moeda(s).",
            ephemeral=True,
        )


class ColorShopView(discord.ui.LayoutView):
    def __init__(self):
        super().__init__(timeout=None)

    container1 = discord.ui.Container(
        discord.ui.Section(
            discord.ui.TextDisplay(
                content=(
                    "﹕🪙 𐔌・𝐋𝐎𝐉𝐀 𝐃𝐄 𝐂𝐎𝐑𝐄𝐒・꒱\n"
                    "˗ˏˋ ｡𖦹 A cada **1h em call** você ganha **1 moeda**. "
                    "Use as moedas para comprar cores gradiente exclusivas."
                )
            ),
            accessory=discord.ui.Thumbnail(
                media="https://cdn.discordapp.com/attachments/1439299374302630011/1469429794818097172/Picsart_26-02-06_17-29-11-387.png?ex=6987a0a3&is=69864f23&hm=47346519a427180b092f40b6ce840429f0fd050d224c5e0d2cd3c8b2d696bd43&",
            ),
        ),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.large),
        discord.ui.TextDisplay(
            content=(
                "###  ╰୭ ˚𝐂𝐎𝐑𝐄𝐒 𝐍𝐀 𝐋𝐎𝐉𝐀... ᵎᵎ\n"
                "── .✦ <@&1439110891659329536> | 6 moedas\n"
                "── .✦ <@&1439111576090050760> | 6 moedas\n"
                "── .✦ <@&1439113714002297014> | 7 moedas\n"
                "── .✦ <@&1439114721360875530> | 7 moedas\n"
                "── .✦ <@&1439115506048303124> | 8 moedas\n"
                "── .✦ <@&1439301268429340894> | 8 moedas\n"
                "── .✦ <@&1439301747364597925> | 9 moedas\n"
                "── .✦ <@&1439302494109827284> | 10 moedas"
            )
        ),
        discord.ui.ActionRow(ColorShopSelect()),
        accent_colour=discord.Colour(15742293),
    )
