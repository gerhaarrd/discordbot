import discord
from discord.ext import commands
from discord import app_commands
import database
import time
from views import ColorShopView

async def register(bot):
    """Registra comandos de voice tracking"""
    
    @bot.tree.command(
        name="moedas",
        description="Mostra seu saldo de moedas de call",
        guild=discord.Object(id=1389947780683796701)
    )
    async def moedas_command(interaction: discord.Interaction):
        try:
            balance = database.get_voice_currency_balance(str(interaction.user.id))
            await interaction.response.send_message(
                f"🪙 Você tem **{balance}** moeda(s) de call.",
                ephemeral=True,
            )
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Erro ao consultar saldo: {e}",
                ephemeral=True,
            )

    @bot.tree.command(
        name="lojacores",
        description="Abre a loja de cores gradiente por moedas de call",
        guild=discord.Object(id=1389947780683796701)
    )
    async def lojacores_command(interaction: discord.Interaction):
        balance = database.get_voice_currency_balance(str(interaction.user.id))
        await interaction.response.send_message(view=ColorShopView(), ephemeral=True)
        await interaction.followup.send(
            f"🪙 Seu saldo atual: **{balance}** moeda(s).",
            ephemeral=True,
        )

    @bot.command()
    async def lojacores(ctx):
        balance = database.get_voice_currency_balance(str(ctx.author.id))
        await ctx.send(f"🪙 Saldo de {ctx.author.mention}: **{balance}** moeda(s).")
        await ctx.send(view=ColorShopView())

    @bot.command()
    async def moedas(ctx):
        balance = database.get_voice_currency_balance(str(ctx.author.id))
        await ctx.send(f"🪙 {ctx.author.mention}, você tem **{balance}** moeda(s).")

    @bot.tree.command(
        name="syncmoedascall",
        description="Sincroniza moedas com as horas já acumuladas em call (Admin only)",
        guild=discord.Object(id=1389947780683796701)
    )
    async def syncmoedascall_command(interaction: discord.Interaction):
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ Apenas administradores podem usar este comando!",
                ephemeral=True,
            )
            return

        try:
            await interaction.response.defer(ephemeral=True)
            added = database.backfill_voice_currency_from_voice_totals()
            await interaction.followup.send(
                f"✅ Sincronização concluída. Moedas adicionadas: **{added}**.",
                ephemeral=True,
            )
        except Exception as e:
            await interaction.followup.send(
                f"❌ Erro ao sincronizar moedas: {e}",
                ephemeral=True,
            )

    @bot.tree.command(
        name="resetvoicetime",
        description="Reseta o tempo de call de todos os usuários (Admin only)",
        guild=discord.Object(id=1389947780683796701)
    )
    async def resetvoicetime_command(interaction: discord.Interaction):
        """Reseta o tempo de call de todos os usuários"""
        
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ Apenas administradores podem usar este comando!",
                ephemeral=True
            )
            return
        
        try:
            await interaction.response.defer()
            
            database.reset_daily_voice_time()
            
            await interaction.followup.send(
                "✅ Tempo de call de todos os usuários foi resetado com sucesso!",
                ephemeral=True
            )
            
        except Exception as e:
            await interaction.followup.send(
                f"❌ Erro ao resetar tempo de call: {e}",
                ephemeral=True
            )
    
    @bot.tree.command(
        name="voicestats",
        description="Mostra suas estatísticas de tempo em call",
        guild=discord.Object(id=1389947780683796701)
    )
    async def voicestats_command(interaction: discord.Interaction):
        """Mostra estatísticas individuais do usuário"""
        
        try:
            await interaction.response.defer()
            
            user_id = str(interaction.user.id)
            user_voice_data = database.get_user_voice_time(user_id)
            
            all_users = database.get_all_voice_times()
            
            user_position = None
            for i, (uid, seconds) in enumerate(all_users, 1):
                if uid == user_id:
                    user_position = i
                    break
            
            active_sessions = database.get_active_voice_sessions()
            in_call_now = user_id in [uid for uid, _ in active_sessions]
            
            time_str = database.format_voice_time(user_voice_data) if user_voice_data else "0h 0m"
            
            embed = discord.Embed(
                title=f"📊 Estatísticas de {interaction.user.display_name}",
                description=f"Aqui estão suas estatísticas de voice call:",
                color=discord.Color.blue()
            )
            
            embed.add_field(
                name="⏱️ Tempo Total em Call",
                value=f"**{time_str}**",
                inline=True
            )
            
            embed.add_field(
                name="🏅 Posição no Ranking",
                value=f"**#{user_position}**" if user_position else "**Não está no ranking**",
                inline=True
            )
            
            embed.add_field(
                name="🎙️ Status Atual",
                value=f"**{'Em call agora' if in_call_now else 'Fora de call'}** 🎧",
                inline=True
            )
            
            total_users = len(all_users)
            embed.add_field(
                name="📈 Informações Adicionais",
                value=f"**Total de usuários:** {total_users}\n**Seu percentil:** {((total_users - user_position + 1) / total_users * 100):.1f}%" if user_position else f"**Total de usuários:** {total_users}",
                inline=False
            )
            
            if user_position and user_position > 3:
                top3 = all_users[:3]
                top3_text = ""
                for i, (uid, seconds) in enumerate(top3, 1):
                    try:
                        member = interaction.guild.get_member(int(uid))
                        name = member.display_name if member else f"User {uid}"
                        time_str = database.format_voice_time(seconds)
                        top3_text += f"**{i}.** {name} - {time_str}\n"
                    except:
                        top3_text += f"**{i}.** User {uid} - {database.format_voice_time(seconds)}\n"
                
                embed.add_field(
                    name="� Top 3 Atual",
                    value=top3_text,
                    inline=False
                )
            
            embed.timestamp = discord.utils.utcnow()
            
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            print(f"Erro no comando voicestats: {e}")
            await interaction.followup.send(
                "❌ Erro ao carregar suas estatísticas!",
                ephemeral=True
            )
    
    @bot.tree.command(
        name="forceranking",
        description="Força a atualização do ranking de voice (Admin only)",
        guild=discord.Object(id=1389947780683796701)
    )
    async def forceranking_command(interaction: discord.Interaction):
        """Força a atualização manual do ranking de voice"""
        
        # Verificar se é admin
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ Apenas administradores podem usar este comando!",
                ephemeral=True
            )
            return
        
        try:
            await interaction.response.defer()
            
            top10 = database.get_top_voice_time(limit=10)
            
            ranking_data = []
            for user_id, seconds in top10:
                try:
                    member = interaction.guild.get_member(int(user_id))
                    mention_or_member = member if member else f"<@{user_id}>"
                    time_str = database.format_voice_time(seconds)
                    ranking_data.append((mention_or_member, time_str))
                except Exception as e:
                    print(f"Erro ao processar usuário {user_id}: {e}")
            
            try:
                ranking_msg = database.get_ranking_message()
                if ranking_msg:
                    channel_id, message_id = ranking_msg
                    channel = interaction.client.get_channel(channel_id)
                    if channel:
                        try:
                            message = await channel.fetch_message(message_id)
                            await message.delete()
                            print(f"🗑️ Mensagem anterior de ranking apagada: {message_id}")
                        except Exception as e:
                            print(f"⚠️ Erro ao apagar mensagem anterior: {e}")
            except Exception as e:
                print(f"⚠️ Erro ao buscar mensagem anterior: {e}")
            
            from views.calltime import RankingCallComponents
            view = RankingCallComponents(ranking_data)
            
            from events.voice_tracker import get_voice_tracker
            voice_tracker = get_voice_tracker()
            if voice_tracker:
                await voice_tracker.update_top_roles(top10)
                channel = interaction.client.get_channel(voice_tracker.ranking_channel_id)
                if channel:
                    message = await channel.send(view=view)
                    database.save_ranking_message(voice_tracker.ranking_channel_id, message.id)
                    print(f"✅ Nova mensagem de ranking enviada: {message.id}")
                    
                    await interaction.followup.send(
                        f"✅ Ranking atualizado com sucesso! {len(top10)} usuários processados.",
                        ephemeral=True
                    )
                else:
                    await interaction.followup.send(
                        "❌ Canal do ranking não encontrado!",
                        ephemeral=True
                    )
            else:
                await interaction.followup.send(
                    "❌ VoiceTracker não encontrado!",
                    ephemeral=True
                )
            
        except Exception as e:
            print(f"Erro no comando forceranking: {e}")
            await interaction.followup.send(
                "❌ Erro ao executar ranking!",
                ephemeral=True
            )
