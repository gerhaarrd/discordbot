import time
import discord
from discord.ext import commands
from views import Components, ColorsView

async def register(bot):
    @bot.command()
    async def send_components(ctx):
        await ctx.send(view=Components())

    @bot.tree.command(name="ping")
    async def ping(interaction: discord.Interaction):
        start = time.perf_counter()
        await interaction.response.send_message("Pinging...")

        elapsed = (time.perf_counter() - start) * 1000

        msg = await interaction.original_response()
        await msg.edit(content=f"{elapsed:.0f}ms — ws {bot.latency*1000:.0f}ms")

    @bot.command()
    async def colors(ctx):
        await ctx.send(view=ColorsView())
