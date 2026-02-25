import time
import discord
from discord.ext import commands
from views import WelcomeComponents, ColorsView, NormalColorsView, RarePingComponents, RarePingView, BumpComponents, HelpView

async def register(bot):
    @bot.command()
    async def send_components(ctx):
        await ctx.send(view=WelcomeComponents())

    @bot.tree.command(name="ping", description="Mede o ping do bot", guild=discord.Object(id=1389947780683796701))
    async def ping(interaction: discord.Interaction):
        start = time.perf_counter()
        await interaction.response.send_message("Pinging...")

        elapsed = (time.perf_counter() - start) * 1000

        msg = await interaction.original_response()
        await msg.edit(content=f"{elapsed:.0f}ms — ws {bot.latency*1000:.0f}ms")

    @bot.command()
    async def colors(ctx):
        await ctx.send(view=ColorsView())

    @bot.command()
    async def normal_colors(ctx):
        await ctx.send(view=NormalColorsView())

    @bot.command()
    async def rareping(ctx):
        await ctx.send(view=RarePingComponents())
        await ctx.send(view=RarePingView())

    @bot.command()
    async def bumpview(ctx):
        await ctx.send(view=BumpComponents())

    @bot.command()
    async def test(ctx):
        await ctx.send("Test command working!")

    @bot.tree.command(
    name="help",
    description="Mostra todos os comandos disponíveis",
    guild=discord.Object(id=1389947780683796701)
)
    async def help_command(interaction: discord.Interaction):
        await interaction.response.send_message(view=HelpView())

    @bot.tree.command(name="testbump", description="Simula um bump done para teste", guild=discord.Object(id=1389947780683796701))
    async def testbump(interaction: discord.Interaction):
        # Verificar se está no canal correto
        if interaction.channel.id != 1389979510975500349:
            await interaction.response.send_message("❌ Use este comando no canal de bumps!", ephemeral=True)
            return

        embed = discord.Embed(
            title="DISBOARD",
            description="Bump done! Check it out!",
            color=discord.Color.green()
        )

        embed.set_author(
            name="DISBOARD",
            icon_url="https://cdn.discordapp.com/icons/302050872383242240/a_???.gif"
        )

        await interaction.response.send_message(embed=embed)
        
        class MockMessage:
            def __init__(self, channel, author_id, embeds):
                self.channel = channel
                self.author = MockAuthor(author_id)
                self.embeds = embeds
        
        class MockAuthor:
            def __init__(self, author_id):
                self.id = author_id
        
        mock_message = MockMessage(interaction.channel, 302050872383242240, [embed])
        
        from events.message_handler import handle_bump_detection
        await handle_bump_detection(interaction.client, mock_message)
