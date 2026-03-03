import discord
from discord.ext import commands
from discord import app_commands
import time
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo
from typing import Dict, List, Optional, Tuple
from functools import lru_cache
import heapq
import database

class ReputationSystem:
    def __init__(self):
        self._ranking_cache = {}
        self._cache_timestamp = 0
        self._cache_ttl = 300  # 5 minutos
        
        # Pré-carregar cache para evitar lentidão na primeira chamada
        self._update_ranking_cache()
        
        # Sistema de níveis e cargos de aura
        self.aura_levels = {
            1: {"rep_required": 150, "role_id": 1476295195006996492, "name": "Aura 1"},
            2: {"rep_required": 300, "role_id": 1476295382257504488, "name": "Aura 2"}, 
            3: {"rep_required": 750, "role_id": 1476295502474641589, "name": "Aura 3"}
        }
    
    def _invalidate_cache(self):
        """Invalida o cache de ranking"""
        self._ranking_cache.clear()
        self._cache_timestamp = 0
    
    def get_user_data(self, user_id: int) -> Dict:
        """Obtém ou cria dados do usuário"""
        user_id_str = str(user_id)
        user_data = database.get_user(user_id_str)
        
        if user_data is None:
            user_data = database.create_user_if_not_exists(user_id_str)
        
        return user_data
    
    @staticmethod
    def get_local_timestamp() -> float:
        return datetime.now().timestamp()
    
    def check_cooldowns(self, giver_id: int, receiver_id: int) -> Tuple[bool, str]:
        """Verifica todos os cooldowns e retorna (pode_dar, motivo)"""
        current_time = time.time()
        giver_id_str = str(giver_id)
        receiver_id_str = str(receiver_id)
        
        # Cooldown global de 3h por giver
        global_cooldown = database.get_cooldown(giver_id_str, "global")
        if global_cooldown and current_time - global_cooldown < 3 * 3600:  # 3 horas
            remaining = timedelta(seconds=int(3 * 3600 - (current_time - global_cooldown)))
            return False, f"Você deve esperar {remaining} para dar reputação novamente."
        
        # Bloqueio mútuo de 3h:
        # Se A deu rep para B recentemente, B não pode dar rep para A por 3h.
        reverse_last_rep = database.get_last_given_timestamp(receiver_id_str, giver_id_str)
        if reverse_last_rep and current_time - reverse_last_rep < 3 * 3600:
            remaining = timedelta(seconds=int(3 * 3600 - (current_time - reverse_last_rep)))
            return False, f"Bloqueio mútuo ativo. Aguarde {remaining} para retribuir reputação para este usuário."
        
        return True, ""
    
    async def add_reputation(self, giver_id: int, receiver_id: int, reason: str = "", guild_id: int = None, guild: discord.Guild = None) -> bool:
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
        guild_id_str = str(guild_id) if guild_id else None
        
        # Adicionar reputação usando database
        success = database.add_rep(giver_id_str, receiver_id_str, guild_id_str, reason)
        
        if success:
            # Atualizar cooldown
            database.update_cooldown(giver_id_str, "global", current_time)
            
            # Invalidar cache
            self._invalidate_cache()
            
            # Atualizar cargos de aura se guild foi fornecida
            if guild:
                receiver_data = self.get_user_data(receiver_id)
                await self.update_user_aura_roles(receiver_id, guild, receiver_data["rep_total"])
        
        return success
    
    def _invalidate_cache(self):
        """Invalida o cache de ranking"""
        self._ranking_cache.clear()
        self._cache_timestamp = 0
    
    def _update_ranking_cache(self):
        """Atualiza o cache de ranking com algoritmo otimizado"""
        current_time = time.time()
        
        # Verificar se cache ainda é válido
        if current_time - self._cache_timestamp < self._cache_ttl and self._ranking_cache:
            return
        
        # Construir cache otimizado usando database
        users_rep = database.get_all_users_rep()
        
        # Armazenar no cache de forma simples
        self._ranking_cache = {
            'top_users': [(int(uid), rep) for uid, rep in users_rep[:100]],  # Cache top 100
            'total_users': len(users_rep)
        }
        self._cache_timestamp = current_time
    
    def get_user_ranking(self, user_id: int) -> Tuple[int, int]:
        """Retorna (reputação, posição no ranking) - Otimizado"""
        # Usar database diretamente - é mais rápido que cache complexo
        user_id_str = str(user_id)
        return database.get_user_ranking(user_id_str)
    
    def get_top_users(self, limit: int = 10) -> List[Tuple[int, int]]:
        """Retorna lista dos top usuários - O(1) com cache"""
        self._update_ranking_cache()
        return self._ranking_cache['top_users'][:limit]
    
    def get_user_history(self, user_id: int, limit: int = 5, page: int = 1) -> List[Dict]:
        """Retorna histórico de reputações recebidas com paginação"""
        user_id_str = str(user_id)
        history = database.get_history(user_id_str, limit=50)  # Buscar mais para paginação
        
        # Paginação
        items_per_page = limit
        start_idx = (page - 1) * items_per_page
        end_idx = start_idx + items_per_page
        
        # Pegar slice do histórico (mais recentes primeiro)
        paginated_history = history[start_idx:end_idx] if start_idx < len(history) else []
        
        # Formatar para exibição
        formatted_history = []
        for entry in paginated_history:
            formatted_history.append({
                "giver_id": int(entry["giver_id"]),
                "reason": entry["reason"],
                "timestamp": entry["timestamp"],
                "date": datetime.fromtimestamp(entry["timestamp"], ZoneInfo('America/Sao_Paulo')).strftime("%d/%m/%Y %H:%M")
            })
        
        return formatted_history
    
    def get_history_stats(self, user_id: int) -> Dict:
        """Retorna estatísticas do histórico"""
        user_id_str = str(user_id)
        history = database.get_history(user_id_str, 1000)  # Buscar até 1000 para estatísticas
        total_history = len(history)
        
        return {
            "total": total_history,
            "pages": (total_history + 4) // 5,  # 5 itens por página
            "has_more": total_history > 5
        }
    
    def get_user_level(self, rep_total: int) -> int:
        """Retorna o nível atual baseado na reputação"""
        level = 0
        for level_num, level_data in self.aura_levels.items():
            if rep_total >= level_data["rep_required"]:
                level = level_num
        return level
    
    def get_next_level_info(self, rep_total: int) -> Optional[Dict]:
        """Retorna informações do próximo nível ou None se já for o máximo"""
        current_level = self.get_user_level(rep_total)
        
        if current_level >= max(self.aura_levels.keys()):
            return None
        
        next_level = current_level + 1
        return {
            "level": next_level,
            "name": self.aura_levels[next_level]["name"],
            "rep_required": self.aura_levels[next_level]["rep_required"],
            "rep_needed": self.aura_levels[next_level]["rep_required"] - rep_total
        }
    
    async def update_user_aura_roles(self, user_id: int, guild: discord.Guild, rep_total: int):
        """Atualiza os cargos de aura do usuário baseado no nível"""
        member = guild.get_member(user_id)
        if not member:
            return
        
        current_level = self.get_user_level(rep_total)
        
        # Remover todos os cargos de aura que não deveria ter
        for level_num, level_data in self.aura_levels.items():
            if level_num > current_level:  # Remover níveis superiores
                role = guild.get_role(level_data["role_id"])
                if role and role in member.roles:
                    try:
                        await member.remove_roles(role)
                    except Exception as e:
                        pass
        
        # Adicionar cargo do nível atual
        if current_level > 0:
            current_role_id = self.aura_levels[current_level]["role_id"]
            role = guild.get_role(current_role_id)
            if role and role not in member.roles:
                try:
                    await member.add_roles(role)
                except Exception as e:
                    pass

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
        success = await rep_system.add_reputation(
            giver_id=interaction.user.id,
            receiver_id=usuario.id,
            reason=motivo,
            guild_id=interaction.guild.id,
            guild=interaction.guild
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
        
        # Adicionar nível e aura atual
        current_level = rep_system.get_user_level(rep_total)
        if current_level > 0:
            aura_name = rep_system.aura_levels[current_level]["name"]
            embed.add_field(
                name="✨ Nível de Aura",
                value=f"**{aura_name}** (Nível {current_level})",
                inline=True
            )
        else:
            embed.add_field(
                name="✨ Nível de Aura",
                value="**Sem aura**",
                inline=True
            )
        
        # Adicionar barra de progresso visual
        if rep_total > 0:
            next_level_info = rep_system.get_next_level_info(rep_total)
            
            if next_level_info:
                # Progresso para próximo nível
                current_level_req = rep_system.aura_levels[next_level_info["level"] - 1]["rep_required"] if next_level_info["level"] > 1 else 0
                progress_needed = next_level_info["rep_required"] - current_level_req
                progress_current = rep_total - current_level_req
                progress = min(progress_current / progress_needed, 1.0)
                
                bar_length = 20
                filled_length = int(bar_length * progress)
                bar = "█" * filled_length + "░" * (bar_length - filled_length)
                
                embed.add_field(
                    name=f"📈 Progresso para {next_level_info['name']}",
                    value=f"[{bar}] {next_level_info['rep_needed']} restantes",
                    inline=False
                )
            else:
                # Já está no nível máximo
                embed.add_field(
                    name="📈 Progresso",
                    value="**Nível Máximo Alcançado!** 🌟",
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
        
        # Responder imediatamente para evitar timeout
        await interaction.response.defer()
        
        top_users = rep_system.get_top_users(10)
        
        if not top_users:
            await interaction.followup.send(
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
        
        embed.set_footer(text=f"Total de {rep_system._ranking_cache.get('total_users', 0)} usuários registrados")
        embed.timestamp = discord.utils.utcnow()
        
        await interaction.followup.send(embed=embed)
    
    @bot.tree.command(
        name="rephistory",
        description="Mostra o histórico de reputações recebidas por um usuário",
        guild=discord.Object(id=1389947780683796701)
    )
    @app_commands.describe(
        usuario="Usuário para consultar (deixe em branco para ver o seu)",
        pagina="Número da página (opcional)"
    )
    async def rephistory_command(
        interaction: discord.Interaction,
        usuario: Optional[discord.Member] = None,
        pagina: int = 1
    ):
        """Mostra histórico de reputações com paginação"""
        
        if pagina < 1:
            await interaction.response.send_message(
                "❌ O número da página deve ser maior que 0!",
                ephemeral=True
            )
            return
        
        target_user = usuario or interaction.user
        history = rep_system.get_user_history(target_user.id, limit=5, page=pagina)
        stats = rep_system.get_history_stats(target_user.id)
        
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
            description=f"Página {pagina} de {stats['pages']} (Total: {stats['total']} reputações)",
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
                name=f"#{(pagina-1)*5 + i} - {giver_name}",
                value=f"📅 **Data:** {entry['date']}{reason_text}",
                inline=False
            )
        
        # Navegação
        navigation_text = ""
        if pagina > 1:
            navigation_text += "⬅️ **Página Anterior** (`/rephistory pagina:{pagina-1}`)"
        if stats['has_more'] and pagina < stats['pages']:
            if navigation_text:
                navigation_text += " | "
            navigation_text += "**Próxima Página** ➡️ (`/rephistory pagina:{pagina+1}`)"
        
        if navigation_text:
            embed.add_field(name="🧭 Navegação", value=navigation_text, inline=False)
        
        embed.set_footer(text=f"ID: {target_user.id} | Mostrando 5 de {stats['total']} reputações")
        embed.timestamp = discord.utils.utcnow()
        
        await interaction.response.send_message(embed=embed)
    
    @bot.tree.command(
        name="replevels",
        description="Mostra todos os níveis de aura e requisitos",
        guild=discord.Object(id=1389947780683796701)
    )
    async def replevels_command(interaction: discord.Interaction):
        """Mostra informações sobre os níveis de aura"""
        
        embed = discord.Embed(
            title="✨ Níveis de Aura",
            description="Sistema progressivo de reputação com cargos exclusivos",
            color=discord.Color.purple()
        )
        
        user_rep, _ = rep_system.get_user_ranking(interaction.user.id)
        current_level = rep_system.get_user_level(user_rep)
        
        for level_num, level_data in rep_system.aura_levels.items():
            # Verificar se usuário já alcançou este nível
            achieved = user_rep >= level_data["rep_required"]
            status_emoji = "✅" if achieved else "🔒"
            
            # Calcular progresso para este nível (se não alcançado)
            if not achieved and level_num > 1:
                prev_level_req = rep_system.aura_levels[level_num - 1]["rep_required"]
                progress_needed = level_data["rep_required"] - prev_level_req
                progress_current = min(user_rep - prev_level_req, 0)
                progress_percent = max(0, min(100, (progress_current / progress_needed) * 100))
            elif not achieved:
                progress_percent = min(100, (user_rep / level_data["rep_required"]) * 100)
            else:
                progress_percent = 100
            
            field_value = f"{status_emoji} **{level_data['rep_required']}** pontos de reputação\n"
            
            if not achieved:
                remaining = level_data["rep_required"] - user_rep
                field_value += f"📊 Progresso: {progress_percent:.1f}%\n"
                field_value += f"⏳ Faltam: **{remaining}** pontos"
            else:
                field_value += f"🎉 **Nível alcançado!**"
            
            embed.add_field(
                name=f"{level_data['name']} (Nível {level_num})",
                value=field_value,
                inline=False
            )
        
        # Adicionar informação do usuário
        embed.add_field(
            name="👤 Seu Status Atual",
            value=f"**Reputação:** {user_rep} pontos\n**Nível:** {current_level}/3",
            inline=False
        )
        
        embed.set_footer(text="Conquiste auras através de reputação recebida!")
        embed.timestamp = discord.utils.utcnow()
        
        await interaction.response.send_message(embed=embed)
