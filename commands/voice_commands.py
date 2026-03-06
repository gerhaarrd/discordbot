import discord
from discord.ext import commands
from discord import app_commands
import database
import time

async def register(bot):
    """Registra comandos de voice tracking"""
    
    @bot.tree.command(
        name="resetvoicetime",
        description="Reseta o tempo de call de todos os usuários (Admin only)",
        guild=discord.Object(id=1389947780683796701)
    )
    async def resetvoicetime_command(interaction: discord.Interaction):
        """Reseta o tempo de call de todos os usuários"""
        
        # Verificar se é admin
        if not interaction.user.guild_permissions.administrator:
            await interaction.response.send_message(
                "❌ Apenas administradores podem usar este comando!",
                ephemeral=True
            )
            return
        
        try:
            # Defer para evitar timeout
            await interaction.response.defer()
            
            # Resetar tempo de call de todos
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
            # Defer para evitar timeout
            await interaction.response.defer()
            
            # Obter dados do usuário
            user_id = str(interaction.user.id)
            user_voice_data = database.get_user_voice_time(user_id)
            
            # Obter ranking completo para calcular posição
            all_users = database.get_all_voice_times()
            
            # Calcular posição do usuário
            user_position = None
            for i, (uid, seconds) in enumerate(all_users, 1):
                if uid == user_id:
                    user_position = i
                    break
            
            # Verificar se está em call agora
            active_sessions = database.get_active_voice_sessions()
            in_call_now = user_id in [uid for uid, _ in active_sessions]
            
            # Formatar tempo
            time_str = database.format_voice_time(user_voice_data) if user_voice_data else "0h 0m"
            
            # Criar embed personalizado
            embed = discord.Embed(
                title=f"📊 Estatísticas de {interaction.user.display_name}",
                description=f"Aqui estão suas estatísticas de voice call:",
                color=discord.Color.blue()
            )
            
            # Estatísticas individuais
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
            
            # Informações adicionais
            total_users = len(all_users)
            embed.add_field(
                name="📈 Informações Adicionais",
                value=f"**Total de usuários:** {total_users}\n**Seu percentil:** {((total_users - user_position + 1) / total_users * 100):.1f}%" if user_position else f"**Total de usuários:** {total_users}",
                inline=False
            )
            
            # Se não está no top 3, mostrar quem está
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
            
            # Obter top 10
            top10 = database.get_top_voice_time(limit=10)
            
            # Obter dados reais dos usuários
            ranking_data = []
            for user_id, seconds in top10:
                try:
                    member = interaction.guild.get_member(int(user_id))
                    if member:
                        time_str = database.format_voice_time(seconds)
                        ranking_data.append((member, time_str))
                except Exception as e:
                    print(f"Erro ao processar usuário {user_id}: {e}")
            
            # Apagar mensagem anterior
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
            
            # Enviar nova mensagem
            from views.calltime import RankingCallComponents
            view = RankingCallComponents(ranking_data)
            
            # Obter canal do ranking
            from events.voice_tracker import get_voice_tracker
            voice_tracker = get_voice_tracker()
            if voice_tracker:
                await voice_tracker.update_top_roles(top10)
                channel = interaction.client.get_channel(voice_tracker.ranking_channel_id)
                if channel:
                    message = await channel.send(view=view)
                    # Salvar ID da nova mensagem
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
