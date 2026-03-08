import discord
import database

SHOP_ITEMS = [
    ("Remover sticker 🚫", "none", 0),
    ("ᯓ 🐉 ‧₊ ᵎᵎ ˚stⁱᶜᵏᵉʳ | 𝐡𝐢𝐝𝐫𝐚⭑꒷꒦", "1479901922273005690", 6),
    ("ᯓ 🦑 ‧₊ ᵎᵎ ˚stⁱᶜᵏᵉʳ | 𝐥𝐞𝐯𝐢𝐚𝐭𝐡𝐚𝐧⭑꒷꒦", "1479898077740666933", 8),
    ("ᯓ ☄️ ‧₊ ᵎᵎ ˚stⁱᶜᵏᵉʳ | 𝐚𝐫𝐦𝐚𝐠𝐞𝐝𝐨𝐦⭑꒷꒦", "1479897267119849726", 10),
    ("ᯓ 🦉 ‧₊ ᵎᵎ ˚stⁱᶜᵏᵉʳ | 𝐬𝐡𝐚𝐝𝐨𝐰⭑꒷꒦", "1479898813131919521", 15),
]

STICKER_ROLE_IDS = [
    1479901922273005690,
    1479898077740666933,
    1479897267119849726,
    1479898813131919521,
]
LEGACY_STICKER_ROLE_IDS = [
    1475153859776221194,
    1475154995778420849,
    1475156042022125729,
    1475156211409358984,
    1475156474136367286,
]
ALL_STICKER_ROLE_IDS = list(dict.fromkeys(STICKER_ROLE_IDS + LEGACY_STICKER_ROLE_IDS))

PRICE_BY_ROLE_ID = {
    int(value): price for _, value, price in SHOP_ITEMS if value != "none"
}


class ColorShopSelect(discord.ui.Select):
    def __init__(self):
        options = []
        for label, value, price in SHOP_ITEMS:
            description = "Sem custo" if value == "none" else f"Custo: {price} Mush"
            options.append(discord.SelectOption(label=label, value=value, description=description))

        super().__init__(
            placeholder="ᯓ★ SELECIONE O STICKER ꒰🛍️‧˚.ᵎᵎ",
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

        roles_to_remove = [role for role in (guild.get_role(rid) for rid in ALL_STICKER_ROLE_IDS) if role and role in member.roles]

        if selected_value == "none":
            if roles_to_remove:
                await member.remove_roles(*roles_to_remove, reason="Loja de stickers: remover sticker")
            database.disable_mush(str(member.id))
            await interaction.response.send_message("Seu sticker foi removido.", ephemeral=True)
            return

        role_id = int(selected_value)
        role = guild.get_role(role_id)
        if role is None:
            await interaction.response.send_message("Cargo de sticker não encontrado.", ephemeral=True)
            return

        if role in member.roles:
            await interaction.response.send_message(
                f"Você já possui {role.mention}.",
                ephemeral=True,
            )
            return

        price = PRICE_BY_ROLE_ID.get(role_id, 0)
        balance = database.get_voice_currency_balance(str(member.id))
        if balance < price:
            await interaction.response.send_message(
                f"Saldo insuficiente. Você tem {balance} Mush e precisa de {price} Mush.",
                ephemeral=True,
            )
            return

        if not database.spend_voice_currency(str(member.id), price):
            await interaction.response.send_message("Não foi possível concluir a compra. Tente novamente.", ephemeral=True)
            return

        if roles_to_remove:
            await member.remove_roles(*roles_to_remove, reason="Loja de stickers: troca de sticker")
        await member.add_roles(role, reason="Loja de stickers: compra")
        database.enable_mush(str(member.id))

        new_balance = database.get_voice_currency_balance(str(member.id))
        await interaction.response.send_message(
            f"Compra concluída: {role.mention}. Saldo atual: {new_balance} Mush.",
            ephemeral=True,
        )


class ColorShopView(discord.ui.LayoutView):
    def __init__(self):
        super().__init__(timeout=None)

    container1 = discord.ui.Container(
        discord.ui.Section(
            discord.ui.TextDisplay(
                content=(
                    "### .🎖 ݁˖ 𝐋𝐎𝐉𝐀—𝐒𝐓𝐈𝐂𝐊𝐄𝐑𝐒 .՞𐦯\n"
                    "˙ . ꒷ Cada **1h** em call rende **1 Mushcoin** no 𝐑𝐞𝐢𝐧𝐨 𝐝𝐨𝐬 𝐕𝐞𝐧𝐭𝐨𝐬. "
                    "Ao juntar uma certa quantidade, você pode trocá-las por um cargo sticker único, "
                    "com cor e ícones exclusivos da **Soul**, marcando sua presença no reino. ꪆৎ"
                )
            ),
            accessory=discord.ui.Thumbnail(
                media="https://cdn.discordapp.com/attachments/1439299374302630011/1479934517656682769/Picsart_26-03-07_17-11-06-039.png?ex=69add7ec&is=69ac866c&hm=94d23e08e7026f480d81fa402ce07875f870efce196d3df821497a522fedb43d&",
            ),
        ),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.large),
        discord.ui.TextDisplay(
            content=(
                "𓂃˖˳ 𝐒𝐓𝐈𝐂𝐊𝐄𝐑𝐒˙\n\n"
                "──★ <@&1479901922273005690>  ̟꒰ **6 Mush**\n"
                "──★ <@&1479898077740666933> ̟ ꒰ **8 Mush**\n"
                "──★ <@&1479897267119849726> ̟ ꒰ **10 Mush**\n"
                "──★ <@&1479898813131919521> ̟  ꒰ **15 Mush**"
            )
        ),
        discord.ui.ActionRow(ColorShopSelect()),
        accent_colour=discord.Colour(16503317),
    )
