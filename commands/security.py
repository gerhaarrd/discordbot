
import discord
from discord import app_commands


async def register(bot):
    @bot.tree.command(name="antiraid", description="Oculta e bloqueia mensagens em todos os canais para @everyone")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def antiraid(interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message("Esse comando só funciona em servidor.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)

        guild = interaction.guild
        everyone = guild.default_role

        overwrite = discord.PermissionOverwrite()
        overwrite.view_channel = False
        overwrite.send_messages = False
        overwrite.send_messages_in_threads = False
        overwrite.add_reactions = False

        ok = 0
        failed = 0
        for channel in guild.channels:
            try:
                await channel.set_permissions(everyone, overwrite=overwrite)
                ok += 1
            except Exception:
                failed += 1

        embed = discord.Embed(
            title="🚨 Anti-raid ativado",
            description="🔒 Lockdown aplicado para o cargo **@everyone** em todos os canais.",
            colour=discord.Colour.red(),
        )
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        embed.add_field(name="✅ Canais atualizados", value=str(ok), inline=True)
        embed.add_field(name="⚠️ Falhas", value=str(failed), inline=True)
        embed.add_field(name="↩️ Desfazer", value="Use `/antiraid_off`", inline=False)
        if failed:
            embed.set_footer(text="Alguns canais podem ter falhado por falta de permissão do bot (Manage Channels) ou por tipo de canal.")

        await interaction.followup.send(embed=embed, ephemeral=True)

    @bot.tree.command(name="antiraid_off", description="Desfaz o anti-raid e volta as permissões padrão do @everyone")
    @app_commands.checks.has_permissions(manage_guild=True)
    async def antiraid_off(interaction: discord.Interaction):
        if interaction.guild is None:
            await interaction.response.send_message("Esse comando só funciona em servidor.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)

        guild = interaction.guild
        everyone = guild.default_role

        ok = 0
        failed = 0
        for channel in guild.channels:
            try:
                await channel.set_permissions(everyone, overwrite=None)
                ok += 1
            except Exception:
                failed += 1

        embed = discord.Embed(
            title="✅ Anti-raid desativado",
            description="🔓 As permissões do **@everyone** voltaram ao padrão (overwrite removido).",
            colour=discord.Colour.green(),
        )
        if guild.icon:
            embed.set_thumbnail(url=guild.icon.url)
        embed.add_field(name="✅ Canais atualizados", value=str(ok), inline=True)
        embed.add_field(name="⚠️ Falhas", value=str(failed), inline=True)
        if failed:
            embed.set_footer(text="Alguns canais podem ter falhado por falta de permissão do bot (Manage Channels) ou por tipo de canal.")

        await interaction.followup.send(embed=embed, ephemeral=True)

    @antiraid.error
    async def antiraid_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
        msg = "Não consegui executar esse comando."
        if isinstance(error, app_commands.errors.MissingPermissions):
            msg = "Você não tem permissão para usar esse comando."

        if interaction.response.is_done():
            await interaction.followup.send(msg, ephemeral=True)
        else:
            await interaction.response.send_message(msg, ephemeral=True)

    @antiraid_off.error
    async def antiraid_off_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
        await antiraid_error(interaction, error)

