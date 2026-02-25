import discord
from discord.ext import commands
from discord import app_commands
import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import os

class ReputationSystem:
    def __init__(self):
        self.data_file = "rep_users.json"
        self.data = self.load_data()
    
    def load_data(self) -> Dict:
        """Carrega os dados do arquivo JSON"""
        try:
            if os.path.exists(self.data_file):
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Erro ao carregar dados de reputação: {e}")
        
        # Estrutura inicial dos dados
        return {
            "users": {},
            "cooldowns": {
                "global": {},  # giver_id -> timestamp
                "pairs": {},   # "giver_id:receiver_id" -> timestamp
                "mutual": {}   # "user1_id:user2_id" -> timestamp
            }
        }
    
    def save_data(self):
        """Salva os dados no arquivo JSON"""
        try:
            with open(self.data_file, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erro ao salvar dados de reputação: {e}")
    
    def get_user_data(self, user_id: int) -> Dict:
        """Obtém ou cria dados do usuário"""
        user_id_str = str(user_id)
        if user_id_str not in self.data["users"]:
            self.data["users"][user_id_str] = {
                "rep_total": 0,
                "history": [],
                "received_from": {},
                "given_to": {}
            }
        return self.data["users"][user_id_str]
    
    def check_cooldowns(self, giver_id: int, receiver_id: int) -> Tuple[bool, str]:
        """Verifica todos os cooldowns e retorna (pode_dar, motivo)"""
        current_time = time.time()
        giver_id_str = str(giver_id)
        receiver_id_str = str(receiver_id)
        
        # Cooldown global de 3h por giver
        if giver_id_str in self.data["cooldowns"]["global"]:
            last_given = self.data["cooldowns"]["global"][giver_id_str]
            if current_time - last_given < 3 * 3600:  # 3 horas
                remaining = timedelta(seconds=int(3 * 3600 - (current_time - last_given)))
                return False, f"Você deve esperar {remaining} para dar reputação novamente."
        
        # Cooldown específico por par (6h)
        pair_key = f"{giver_id_str}:{receiver_id_str}"
        if pair_key in self.data["cooldowns"]["pairs"]:
            last_given = self.data["cooldowns"]["pairs"][pair_key]
            if current_time - last_given < 6 * 3600:  # 6 horas
                remaining = timedelta(seconds=int(6 * 3600 - (current_time - last_given)))
                return False, f"Você já deu reputação para este usuário recentemente. Aguarde {remaining}."
        
        # Bloquear rep mútua (3h)
        mutual_key1 = f"{giver_id_str}:{receiver_id_str}"
        mutual_key2 = f"{receiver_id_str}:{giver_id_str}"
        
        if mutual_key2 in self.data["cooldowns"]["mutual"]:
            last_mutual = self.data["cooldowns"]["mutual"][mutual_key2]
            if current_time - last_mutual < 3 * 3600:  # 3 horas
                remaining = timedelta(seconds=int(3 * 3600 - (current_time - last_mutual)))
                return False, f"Este usuário deu reputação para você recentemente. Aguarde {remaining} para retribuir."
        
        return True, ""
    
    def add_reputation(self, giver_id: int, receiver_id: int, reason: str = "", guild_id: int = None) -> bool:
        """Adiciona reputação se todas as validações passarem"""
        # Verificar se não está dando para si mesmo
        if giver_id == receiver_id:
            return False
        
        # Verificar cooldowns
        can_give, reason = self.check_cooldowns(giver_id, receiver_id)
        if not can_give:
            return False
        
        current_time = time.time()
        giver_id_str = str(giver_id)
        receiver_id_str = str(receiver_id)
        
        # Obter/atualizar dados dos usuários
        receiver_data = self.get_user_data(receiver_id)
        giver_data = self.get_user_data(giver_id)
        
        # Adicionar reputação
        receiver_data["rep_total"] += 1
        
        # Adicionar ao histórico
        history_entry = {
            "giver_id": giver_id_str,
            "receiver_id": receiver_id_str,
            "reason": reason,
            "timestamp": current_time,
            "guild_id": str(guild_id) if guild_id else None
        }
        
        receiver_data["history"].append(history_entry)
        
        # Manter apenas últimos 50 históricos para não sobrecarregar
        if len(receiver_data["history"]) > 50:
            receiver_data["history"] = receiver_data["history"][-50:]
        
        # Atualizar registros de quem deu/recebeu
        receiver_data["received_from"][giver_id_str] = current_time
        giver_data["given_to"][receiver_id_str] = current_time
        
        # Atualizar cooldowns
        self.data["cooldowns"]["global"][giver_id_str] = current_time
        self.data["cooldowns"]["pairs"][f"{giver_id_str}:{receiver_id_str}"] = current_time
        self.data["cooldowns"]["mutual"][f"{giver_id_str}:{receiver_id_str}"] = current_time
        
        # Salvar dados
        self.save_data()
        
        return True
    
    def get_user_ranking(self, user_id: int) -> Tuple[int, int]:
        """Retorna (reputação, posição no ranking)"""
        user_data = self.get_user_data(user_id)
        rep_total = user_data["rep_total"]
        
        # Calcular posição no ranking
        all_users = [(uid, data["rep_total"]) for uid, data in self.data["users"].items()]
        all_users.sort(key=lambda x: x[1], reverse=True)
        
        position = 1
        for uid, rep in all_users:
            if int(uid) == user_id:
                break
            position += 1
        
        return rep_total, position
    
    def get_top_users(self, limit: int = 10) -> List[Tuple[int, int]]:
        """Retorna lista dos top usuários (user_id, rep_total)"""
        all_users = [(int(uid), data["rep_total"]) for uid, data in self.data["users"].items()]
        all_users.sort(key=lambda x: x[1], reverse=True)
        return all_users[:limit]
    
    def get_user_history(self, user_id: int, limit: int = 5) -> List[Dict]:
        """Retorna histórico de reputações recebidas"""
        user_data = self.get_user_data(user_id)
        history = user_data["history"][-limit:]  # Últimos registros
        
        # Formatar para exibição
        formatted_history = []
        for entry in reversed(history):  # Mais recentes primeiro
            formatted_history.append({
                "giver_id": int(entry["giver_id"]),
                "reason": entry["reason"],
                "timestamp": entry["timestamp"],
                "date": datetime.fromtimestamp(entry["timestamp"]).strftime("%d/%m/%Y %H:%M")
            })
        
        return formatted_history

# Instância global do sistema
rep_system = ReputationSystem()

async def register(bot):
    """Registra todos os comandos de reputação"""
    
    @bot.tree.command(
        name="rep",
        description="Dá um ponto de reputação para um usuário",
        guild=discord.Object(id=1389947780683796701)
    )
    @app_commands.describe(
        usuario="Usuário que receberá a reputação",
        motivo="Motivo da reputação (opcional)"
    )
    async def rep_command(
        interaction: discord.Interaction,
        usuario: discord.Member,
        motivo: str = ""
    ):
        """Comando principal para dar reputação"""
        
        # Validações básicas
        if usuario.id == interaction.user.id:
            await interaction.response.send_message(
                "❌ Você não pode dar reputação para si mesmo!",
                ephemeral=True
            )
            return
        
        if usuario.bot:
            await interaction.response.send_message(
                "❌ Você não pode dar reputação para bots!",
                ephemeral=True
            )
            return
        
        # Tentar adicionar reputação
        success = rep_system.add_reputation(
            giver_id=interaction.user.id,
            receiver_id=usuario.id,
            reason=motivo,
            guild_id=interaction.guild.id
        )
        
        if success:
            # Obter nova reputação do usuário
            new_rep, position = rep_system.get_user_ranking(usuario.id)
            
            embed = discord.Embed(
                title="✅ Reputação Adicionada!",
                description=f"**{interaction.user.mention}** deu reputação para **{usuario.mention}**!",
                color=discord.Color.green()
            )
            
            if motivo:
                embed.add_field(name="📝 Motivo", value=motivo, inline=False)
            
            embed.add_field(
                name="📊 Estatísticas",
                value=f"**Reputação total:** {new_rep}\n**Posição no ranking:** #{position}",
                inline=False
            )
            
            embed.set_footer(text=f"ID: {usuario.id}")
            embed.timestamp = discord.utils.utcnow()
            
            await interaction.response.send_message(embed=embed)
        else:
            # Verificar motivo da falha
            can_give, reason = rep_system.check_cooldowns(interaction.user.id, usuario.id)
            
            embed = discord.Embed(
                title="❌ Não foi possível dar reputação",
                description=reason,
                color=discord.Color.red()
            )
            
            await interaction.response.send_message(embed=embed, ephemeral=True)
    
    @bot.tree.command(
        name="reppoints",
        description="Mostra a reputação e ranking de um usuário",
        guild=discord.Object(id=1389947780683796701)
    )
    @app_commands.describe(
        usuario="Usuário para consultar (deixe em branco para ver o seu)"
    )
    async def reppoints_command(
        interaction: discord.Interaction,
        usuario: Optional[discord.Member] = None
    ):
        """Mostra pontos de reputação"""
        
        target_user = usuario or interaction.user
        rep_total, position = rep_system.get_user_ranking(target_user.id)
        
        embed = discord.Embed(
            title=f"📊 Reputação de {target_user.display_name}",
            color=discord.Color.blue()
        )
        
        embed.set_thumbnail(url=target_user.display_avatar.url)
        
        embed.add_field(
            name="💎 Reputação Total",
            value=f"**{rep_total}** pontos",
            inline=True
        )
        
        embed.add_field(
            name="🏆 Posição no Ranking",
            value=f"**#{position}**",
            inline=True
        )
        
        # Adicionar barra de progresso visual
        if rep_total > 0:
            progress = min(rep_total / 100, 1.0)  # Baseado em 100 pontos como máximo visual
            bar_length = 20
            filled_length = int(bar_length * progress)
            bar = "█" * filled_length + "░" * (bar_length - filled_length)
            embed.add_field(
                name="📈 Progresso",
                value=f"[{bar}] {rep_total}/100",
                inline=False
            )
        
        embed.set_footer(text=f"ID: {target_user.id}")
        embed.timestamp = discord.utils.utcnow()
        
        await interaction.response.send_message(embed=embed)
    
    @bot.tree.command(
        name="reptop",
        description="Mostra o ranking dos 10 usuários com mais reputação",
        guild=discord.Object(id=1389947780683796701)
    )
    async def reptop_command(interaction: discord.Interaction):
        """Mostra o ranking top 10"""
        
        top_users = rep_system.get_top_users(10)
        
        if not top_users:
            await interaction.response.send_message(
                "❌ Nenhum usuário com reputação encontrada ainda!",
                ephemeral=True
            )
            return
        
        embed = discord.Embed(
            title="🏆 Ranking de Reputação - Top 10",
            description="Usuários com maior reputação do servidor",
            color=discord.Color.gold()
        )
        
        # Criar medalhas para top 3
        medals = ["🥇", "🥈", "🥉"]
        
        ranking_text = ""
        for i, (user_id, rep_total) in enumerate(top_users, 1):
            try:
                user = await interaction.guild.fetch_member(user_id)
                user_name = user.display_name
                avatar_url = user.display_avatar.url
            except:
                user_name = f"Usuário {user_id}"
                avatar_url = None
            
            medal = medals[i-1] if i <= 3 else f"**{i}.**"
            ranking_text += f"{medal} **{user_name}** - {rep_total} pontos\n"
        
        embed.add_field(name="📋 Ranking", value=ranking_text, inline=False)
        
        # Adicionar informações do autor no ranking
        my_rep, my_position = rep_system.get_user_ranking(interaction.user.id)
        embed.add_field(
            name="📍 Sua Posição",
            value=f"**#{my_position}** com {my_rep} pontos",
            inline=False
        )
        
        embed.set_footer(text=f"Total de {len(rep_system.data['users'])} usuários registrados")
        embed.timestamp = discord.utils.utcnow()
        
        await interaction.response.send_message(embed=embed)
    
    @bot.tree.command(
        name="rephistory",
        description="Mostra o histórico de reputações recebidas por um usuário",
        guild=discord.Object(id=1389947780683796701)
    )
    @app_commands.describe(
        usuario="Usuário para consultar (deixe em branco para ver o seu)"
    )
    async def rephistory_command(
        interaction: discord.Interaction,
        usuario: Optional[discord.Member] = None
    ):
        """Mostra histórico de reputações"""
        
        target_user = usuario or interaction.user
        history = rep_system.get_user_history(target_user.id, 5)
        
        if not history:
            embed = discord.Embed(
                title=f"📜 Histórico de {target_user.display_name}",
                description="Nenhuma reputação recebida ainda.",
                color=discord.Color.greyple()
            )
            await interaction.response.send_message(embed=embed)
            return
        
        embed = discord.Embed(
            title=f"📜 Histórico de Reputação - {target_user.display_name}",
            description="Últimas 5 reputações recebidas",
            color=discord.Color.purple()
        )
        
        embed.set_thumbnail(url=target_user.display_avatar.url)
        
        for i, entry in enumerate(history, 1):
            try:
                giver = await interaction.guild.fetch_member(entry["giver_id"])
                giver_name = giver.display_name
            except:
                giver_name = f"Usuário {entry['giver_id']}"
            
            reason_text = f"\n📝 **Motivo:** {entry['reason']}" if entry['reason'] else ""
            
            embed.add_field(
                name=f"#{i} - {giver_name}",
                value=f"📅 **Data:** {entry['date']}{reason_text}",
                inline=False
            )
        
        embed.set_footer(text=f"ID: {target_user.id} | Mostrando últimas 5 de {len(rep_system.get_user_data(target_user.id)['history'])} reputações")
        embed.timestamp = discord.utils.utcnow()
        
        await interaction.response.send_message(embed=embed)
    
    print("Sistema de reputação carregado com sucesso!")
