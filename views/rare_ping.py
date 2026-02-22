import discord

role_id = 1459297833126596608

class RarePingButton(discord.ui.Button):
    def __init__(self):
        super().__init__(
            label="꒰🧨°‧",
            style=discord.ButtonStyle.secondary,
            custom_id="rare_ping_toggle"
        )
    
    async def callback(self, interaction: discord.Interaction):
        member = interaction.user
        role = interaction.guild.get_role(role_id)
        
        if not role:
            await interaction.response.send_message("❌ Cargo não encontrado!", ephemeral=True)
            return
        
        if role in member.roles:
            await member.remove_roles(role)
            await interaction.response.send_message("✅ Você não receberá mais pings de Pokémon raros!", ephemeral=True)
        else:
            await member.add_roles(role)
            await interaction.response.send_message("✅ Você agora receberá pings de Pokémon raros!", ephemeral=True)

class Components(discord.ui.LayoutView):
    def __init__(self):
        super().__init__(timeout=None)

    container1 = discord.ui.Container(
        discord.ui.MediaGallery(
            discord.MediaGalleryItem(
                media="https://cdn.discordapp.com/attachments/1465905808935223416/1472052760047259790/POKEMON_3.png?ex=699c6037&is=699b0eb7&hm=beebb3030c9aacc665e4e20310354fa7840addf69165821a33d0ccf546aa1531&",
            ),
        ),
        discord.ui.Separator(visible=True, spacing=discord.SeparatorSpacing.large),
        discord.ui.TextDisplay(
            content="ᯓ★ No 𝐑𝐞𝐢𝐧𝐨 𝐝𝐨𝐬 𝐕𝐞𝐧𝐭𝐨𝐬, quando um Pokémon raro cruza o véu do acaso, este ping desperta aqueles que escolheram ouvir. \n\n**Ao interagir com o ꒰🧨°‧ abaixo**, você ativa a notificação especial e passa a receber alertas sempre que um **pokémon raro** aparecer no spawn do PokeTwo. ˎˊ˗"
        ),
        accent_colour=discord.Colour(15419688),
    )

class RarePingView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
        self.add_item(RarePingButton())