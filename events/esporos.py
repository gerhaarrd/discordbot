import discord
import asyncio

role_id = 1475160585078308895
channel1 = 1389947781778772132
channel2 = 1476989026274902198
AUTO_DELETE_SECONDS = 8 * 60


class Components(discord.ui.LayoutView):    
    container1 = discord.ui.Container(
        discord.ui.Section(
            discord.ui.TextDisplay(content="### ᯓ★ Seja Esporos! ⋅ ˚✮\nAdicione **.gg/soulll** em sua bio ou nota do Discord e receba o cargo ദ്ദി 𝐄𝐒𝐏𝐎𝐑𝐎𝐒.ᵍᵍ/ˢᵒᵘˡˡˡ ꒱ 🍄 ᯓ★ com ícone e cor gradiente **exclusiva!!** Simples, né?\n\nᝰ.ᐟ Entre em contato com a equipe para reivindicar o cargo... ‧🌿｡⋆"),
            accessory=discord.ui.Thumbnail(
                media="https://cdn.discordapp.com/attachments/1452857118934827221/1475184019271454953/file_0000000016ec71f5b802732d689c371b.png?ex=699c8fad&is=699b3e2d&hm=cddd69cc21dc99b601313304acdefbbdf1440f9495760590e6b5a240a3789365&",
            ),
        ),
        discord.ui.MediaGallery(
            discord.MediaGalleryItem(
                media="https://cdn.discordapp.com/attachments/1439299374302630011/1475191024757379205/1771783340263.png?ex=699c9634&is=699b44b4&hm=cf235d7b4aa5841c23f381d0b2aa67892314067918ab61b09ce313dc5ce3aaa6&",
            ),
        ),
        accent_colour=discord.Colour(15074687),
    )


async def register(bot):
    @bot.command()
    async def testesporos(ctx):
        """Testa o envio da mensagem dos Esporos"""
        try:
            await ctx.send(view=Components())
            await ctx.send("✅ Mensagem de teste enviada com sucesso!")
        except Exception as e:
            await ctx.send(f"❌ Erro ao enviar mensagem: {e}")
    
    async def esporos_task():
        await bot.wait_until_ready()
        
        async def send_esporos(channel_id: int, label: str):
            channel = bot.get_channel(channel_id)
            if channel is None:
                try:
                    channel = await bot.fetch_channel(channel_id)
                except Exception as e:
                    print(f"Error fetching channel {label}: {e}")
                    return

            try:
                await channel.send(view=Components(), delete_after=AUTO_DELETE_SECONDS)
                print(f"Esporos message sent to channel {label}")
            except Exception as e:
                print(f"Error sending to channel {label}: {e}")

        await send_esporos(channel1, "1 (startup)")
        await send_esporos(channel2, "2 (startup)")

        while not bot.is_closed():
            await asyncio.sleep(3 * 60 * 60)
            await send_esporos(channel1, "1")
            await send_esporos(channel2, "2")
    
    bot.loop.create_task(esporos_task())
