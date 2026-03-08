import discord
from discord.ext import tasks
import time
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import database

voice_tracker_instance = None

def get_voice_tracker():
    return voice_tracker_instance

class VoiceTracker:
    def __init__(self, bot):
        self.bot = bot
        self.guild_id = 1389947780683796701
        self.ranking_channel_id = 1477861769497149522
        self.top_roles = {
            1: 1478725893403836536,
            2: 1478726585480908994,
            3: 1478727489554612265,
        }

        database.create_voice_tables()
        database.create_ranking_message_table()

        self.voice_ranking_task.start()

    async def _get_guild_member(self, user_id: int):
        guild = self.bot.get_guild(self.guild_id)
        if not guild:
            return None

        member = guild.get_member(user_id)
        if member:
            return member

        try:
            return await guild.fetch_member(user_id)
        except Exception:
            return None
    
    async def initialize(self):
        print("🚀 Inicializando VoiceTracker...")
        added = database.backfill_voice_currency_from_voice_totals()
        print(f"🪙 Backfill de moedas concluído. Moedas adicionadas: {added}")
        await self.send_initial_ranking()
        print("✅ VoiceTracker inicializado!")
    
    async def send_initial_ranking(self):
        try:
            print("🔍 Verificando mensagem de ranking...")

            try:
                ranking_msg = database.get_ranking_message()
                if ranking_msg:
                    channel_id, message_id = ranking_msg
                    channel = self.bot.get_channel(channel_id)
                    if channel:
                        try:
                            message = await channel.fetch_message(message_id)
                            await message.delete()
                            print(f"🗑️ Mensagem anterior de ranking apagada: {message_id}")
                        except Exception as e:
                            print(f"⚠️ Erro ao apagar mensagem anterior: {e}")
            except Exception as e:
                print(f"⚠️ Erro ao buscar mensagem anterior: {e}")
            
            print("📤 Enviando nova mensagem de ranking...")

            top10 = database.get_top_voice_time(limit=10)
            print(f"📊 Top 10 encontrado: {len(top10)} usuários")

            ranking_data = []
            for user_id, seconds in top10:
                try:
                    member = await self._get_guild_member(int(user_id))
                    mention_or_member = member if member else f"<@{user_id}>"
                    time_str = database.format_voice_time(seconds)
                    ranking_data.append((mention_or_member, time_str))
                except Exception as e:
                    print(f"Erro ao processar usuário {user_id}: {e}")

            await self.update_top_roles(top10)

            from views.calltime import RankingCallComponents
            view = RankingCallComponents(ranking_data)
            channel = self.bot.get_channel(self.ranking_channel_id)
            if channel:
                message = await channel.send(view=view)
                database.save_ranking_message(self.ranking_channel_id, message.id)
                print(f"✅ Nova mensagem de ranking enviada: {message.id}")
            else:
                print(f"❌ Canal {self.ranking_channel_id} não encontrado")
                
        except Exception as e:
            print(f"❌ Erro ao enviar mensagem de ranking: {e}")
    
    def cleanup(self):
        self.voice_ranking_task.cancel()
    
    @tasks.loop(minutes=1)
    async def voice_ranking_task(self):
        try:
            now = datetime.now(ZoneInfo('America/Sao_Paulo'))

            if now.hour == 4 and now.minute == 0:
                today_str = now.strftime('%Y-%m-%d')
                last_run = database.get_last_voice_ranking_run()
                
                if last_run != today_str:
                    await self.execute_daily_ranking(today_str)
        except Exception as e:
            print(f"Erro no voice_ranking_task: {e}")
    
    @voice_ranking_task.before_loop
    async def before_voice_ranking_task(self):
        await self.bot.wait_until_ready()
    
    async def execute_daily_ranking(self, date_str: str):
        try:
            print(f"Executando ranking de voice do dia {date_str}")

            top10 = database.get_top_voice_time(limit=10)

            if not top10:
                print("Nenhum usuário com tempo em call registrado")
                database.update_last_voice_ranking_run(date_str)
                return

            ranking_data = []
            for user_id, seconds in top10:
                try:
                    member = await self._get_guild_member(int(user_id))
                    mention_or_member = member if member else f"<@{user_id}>"
                    time_str = database.format_voice_time(seconds)
                    ranking_data.append((mention_or_member, time_str))
                except Exception as e:
                    print(f"Erro ao processar usuário {user_id}: {e}")

            await self.update_top_roles(top10)

            try:
                ranking_msg = database.get_ranking_message()
                if ranking_msg:
                    channel_id, message_id = ranking_msg
                    channel = self.bot.get_channel(channel_id)
                    if channel:
                        try:
                            message = await channel.fetch_message(message_id)
                            await message.delete()
                            print(f"Mensagem anterior de ranking apagada: {message_id}")
                        except Exception as e:
                            print(f"Erro ao apagar mensagem anterior: {e}")
            except Exception as e:
                print(f"Erro ao buscar mensagem anterior: {e}")

            from views.calltime import RankingCallComponents
            view = RankingCallComponents(ranking_data)
            channel = self.bot.get_channel(self.ranking_channel_id)
            if channel:
                message = await channel.send(view=view)
                database.save_ranking_message(self.ranking_channel_id, message.id)
                print(f"Nova mensagem de ranking enviada: {message.id}")
            else:
                print(f"Canal {self.ranking_channel_id} não encontrado")

            database.update_last_voice_ranking_run(date_str)

            print(f"Ranking de voice atualizado: {len(top10)} usuários")

        except Exception as e:
            print(f"Erro no ranking diário: {e}")
    
    async def generate_ranking_message(self, top10: list) -> str:
        lines = []

        for i, (user_id, seconds) in enumerate(top10, 1):
            try:
                user = await self._get_guild_member(int(user_id))

                user_mention = user.mention if user else f"<@{user_id}>"
                time_formatted = database.format_voice_time(seconds)

                lines.append(f"@{user_mention} [{time_formatted}]")

            except Exception as e:
                print(f"Erro ao processar usuário {user_id}: {e}")
                lines.append(f"@<@{user_id}> [{database.format_voice_time(seconds)}]")

        while len(lines) < 10:
            lines.append("@usuário [0h 0m]")

        return "\n".join(lines)

    async def update_top_roles(self, top_users: list):
        guild = self.bot.get_guild(self.guild_id)
        if not guild:
            print(f"❌ Guild {self.guild_id} não encontrada para atualizar cargos de ranking")
            return

        expected_members = {}
        for position, role_id in self.top_roles.items():
            if len(top_users) >= position:
                user_id = int(top_users[position - 1][0])
                expected_members[role_id] = user_id
            else:
                expected_members[role_id] = None

        for role_id, expected_user_id in expected_members.items():
            role = guild.get_role(role_id)
            if not role:
                print(f"⚠️ Cargo {role_id} não encontrado")
                continue

            for member in list(role.members):
                if expected_user_id is None or member.id != expected_user_id:
                    try:
                        await member.remove_roles(role, reason="Atualização automática do ranking de voice")
                    except Exception as e:
                        print(f"Erro removendo cargo {role_id} de {member.id}: {e}")

            if expected_user_id is not None:
                member = await self._get_guild_member(expected_user_id)
                if not member:
                    print(f"⚠️ Membro {expected_user_id} não encontrado para o cargo {role_id}")
                    continue
                if role not in member.roles:
                    try:
                        await member.add_roles(role, reason="Atualização automática do ranking de voice")
                    except Exception as e:
                        print(f"Erro adicionando cargo {role_id} para {expected_user_id}: {e}")

async def setup(bot):
    global voice_tracker_instance
    voice_tracker_instance = VoiceTracker(bot)
    
    @bot.event
    async def on_voice_state_update(member, before, after):
        try:
            if member.bot:
                return

            if before.channel is None and after.channel is not None:
                await handle_voice_join(member, after.channel)

            elif before.channel is not None and after.channel is None:
                await handle_voice_leave(member, before.channel)

        except Exception as e:
            print(f"Erro em on_voice_state_update: {e}")

async def handle_voice_join(member, channel):
    try:
        user_id_str = str(member.id)
        joined_at = time.time()

        success = database.start_voice_session(user_id_str, joined_at)

        if success:
            print(f"{member.display_name} entrou na call {channel.name}")
        else:
            print(f"{member.display_name} já estava em call (ignorado)")

    except Exception as e:
        print(f"Erro ao handle_voice_join: {e}")

async def handle_voice_leave(member, channel):
    try:
        user_id_str = str(member.id)
        left_at = time.time()

        session_duration = database.end_voice_session(user_id_str, left_at)

        if session_duration is not None:
            time_formatted = database.format_voice_time(session_duration)
            earned_coins = database.sync_user_voice_currency_with_voice_total(user_id_str)
            print(f"{member.display_name} saiu da call {channel.name} - Tempo: {time_formatted}")
            if earned_coins > 0:
                print(f"{member.display_name} ganhou {earned_coins} moeda(s) de call")
        else:
            print(f"{member.display_name} saiu da call mas não tinha sessão ativa")

    except Exception as e:
        print(f"Erro ao handle_voice_leave: {e}")

async def register(bot):
    await setup(bot)
