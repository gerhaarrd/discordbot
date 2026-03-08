import time
import discord
from discord.ext import commands
from views import WelcomeComponents, ColorsView, NormalColorsView, RarePingComponents, RarePingView, BumpComponents, HelpView, ColorShopView

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

    @bot.command()
    async def stickershop(ctx):
        await ctx.send(view=ColorShopView())

    @bot.tree.command(
    name="help",
    description="Mostra todos os comandos disponíveis",
    guild=discord.Object(id=1389947780683796701)
)
    async def help_command(interaction: discord.Interaction):
        await interaction.response.send_message(view=HelpView())
