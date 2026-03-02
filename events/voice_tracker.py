import discord
from discord.ext import tasks
import time
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
import database

# Instância global do VoiceTracker
voice_tracker_instance = None

def get_voice_tracker():
    """Retorna a instância global do VoiceTracker"""
    return voice_tracker_instance

class VoiceTracker:
    def __init__(self, bot):
        self.bot = bot
        self.ranking_channel_id = 1477857188667068467  # ID do canal para ranking
        
        # Criar tabelas do voice tracking
        database.create_voice_tables()
        database.create_ranking_message_table()
        
        # Iniciar task de ranking
        self.voice_ranking_task.start()
    
    async def initialize(self):
        """Inicialização assíncrona - envia mensagem inicial se não existir"""
        print("🚀 Inicializando VoiceTracker...")
        await self.send_initial_ranking()
        print("✅ VoiceTracker inicializado!")
    
    async def send_initial_ranking(self):
        """Apaga mensagem anterior e envia nova mensagem de ranking"""
        try:
            print("🔍 Verificando mensagem de ranking...")
            
            # Tentar apagar mensagem anterior (se existir)
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
            
            # Obter dados atuais
            top5 = database.get_top5_voice_time()
            print(f"📊 Top 5 encontrado: {len(top5)} usuários")
            
            # Obter dados reais dos usuários
            ranking_data = []
            for user_id, seconds in top5:
                try:
                    member = self.bot.get_user(int(user_id))
                    if not member:
                        # Tentar buscar do guild se não encontrar no cache
                        guild = self.bot.get_guild(1389947780683796701)
                        member = guild.get_member(int(user_id)) if guild else None
                    
                    if member:
                        time_str = database.format_voice_time(seconds)
                        ranking_data.append((member, time_str))
                except Exception as e:
                    print(f"Erro ao processar usuário {user_id}: {e}")
            
            # Enviar nova mensagem
            from views.calltime import RankingCallComponents
            view = RankingCallComponents(ranking_data)
            channel = self.bot.get_channel(self.ranking_channel_id)
            if channel:
                message = await channel.send(view=view)
                # Salvar ID da nova mensagem
                database.save_ranking_message(self.ranking_channel_id, message.id)
                print(f"✅ Nova mensagem de ranking enviada: {message.id}")
            else:
                print(f"❌ Canal {self.ranking_channel_id} não encontrado")
                
        except Exception as e:
            print(f"❌ Erro ao enviar mensagem de ranking: {e}")
    
    def cleanup(self):
        """Limpa resources quando o bot desliga"""
        self.voice_ranking_task.cancel()
    
    @tasks.loop(minutes=1)
    async def voice_ranking_task(self):
        """Task que verifica se é hora de executar o ranking (4:00 AM)"""
        try:
            # Obter horário local do servidor (America/Sao_Paulo)
            now = datetime.now(ZoneInfo('America/Sao_Paulo'))
            
            # Verificar se são 4:00 AM e se ainda não executou hoje
            if now.hour == 4 and now.minute == 0:
                today_str = now.strftime('%Y-%m-%d')
                last_run = database.get_last_voice_ranking_run()
                
                if last_run != today_str:
                    await self.execute_daily_ranking(today_str)
        except Exception as e:
            print(f"Erro no voice_ranking_task: {e}")
    
    @voice_ranking_task.before_loop
    async def before_voice_ranking_task(self):
        """Espera o bot estar pronto antes de iniciar"""
        await self.bot.wait_until_ready()
    
    async def execute_daily_ranking(self, date_str: str):
        """Executa o ranking diário de tempo em call"""
        try:
            print(f"Executando ranking de voice do dia {date_str}")
            
            # Obter top 5 usuários
            top5 = database.get_top5_voice_time()
            
            if not top5:
                print("Nenhum usuário com tempo em call registrado")
                database.update_last_voice_ranking_run(date_str)
                # NÃO resetar tempo de call
                return
            
            # Obter dados reais dos usuários
            ranking_data = []
            for user_id, seconds in top5:
                try:
                    member = self.bot.get_user(int(user_id))
                    if not member:
                        # Tentar buscar do guild se não encontrar no cache
                        guild = self.bot.get_guild(1389947780683796701)
                        member = guild.get_member(int(user_id)) if guild else None
                    
                    if member:
                        time_str = database.format_voice_time(seconds)
                        ranking_data.append((member, time_str))
                except Exception as e:
                    print(f"Erro ao processar usuário {user_id}: {e}")
            
            # Tentar apagar mensagem anterior
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
            
            # Enviar nova mensagem
            from views.calltime import RankingCallComponents
            view = RankingCallComponents(ranking_data)
            channel = self.bot.get_channel(self.ranking_channel_id)
            if channel:
                message = await channel.send(view=view)
                # Salvar ID da nova mensagem
                database.save_ranking_message(self.ranking_channel_id, message.id)
                print(f"Nova mensagem de ranking enviada: {message.id}")
            else:
                print(f"Canal {self.ranking_channel_id} não encontrado")
            
            # Atualizar controle (mas NÃO resetar tempo de call)
            database.update_last_voice_ranking_run(date_str)
            
            print(f"Ranking de voice atualizado: {len(top5)} usuários")
            
        except Exception as e:
            print(f"Erro no ranking diário: {e}")
    
    async def generate_ranking_message(self, top5: list) -> str:
        """Gera a mensagem formatada do ranking"""
        lines = []
        
        for i, (user_id, seconds) in enumerate(top5, 1):
            try:
                # Obter objeto do usuário
                user = self.bot.get_user(int(user_id))
                if not user:
                    # Tentar buscar do guild se não encontrar no cache
                    guild = self.bot.get_guild(1389947780683796701)
                    if guild:
                        user = guild.get_member(int(user_id))
                
                user_mention = user.mention if user else f"<@{user_id}>"
                time_formatted = database.format_voice_time(seconds)
                
                lines.append(f"@{user_mention} [{time_formatted}]")
                
            except Exception as e:
                print(f"Erro ao processar usuário {user_id}: {e}")
                lines.append(f"@<@{user_id}> [{database.format_voice_time(seconds)}]")
        
        # Preencher com espaços vazios se tiver menos de 5
        while len(lines) < 5:
            lines.append("@usuário [0h 0m]")
        
        return "\n".join(lines)

async def setup(bot):
    """Setup do voice tracker"""
    global voice_tracker_instance
    voice_tracker_instance = VoiceTracker(bot)
    
    @bot.event
    async def on_voice_state_update(member, before, after):
        """Monitora eventos de entrada/saída de canais de voz"""
        try:
            # Ignorar bots
            if member.bot:
                return
            
            # Verificar se entrou em algum canal de voz
            if before.channel is None and after.channel is not None:
                # Entrou em call
                await handle_voice_join(member, after.channel)
            
            # Verificar se saiu de canal de voz (saiu totalmente, não apenas mudou de canal)
            elif before.channel is not None and after.channel is None:
                # Saiu da call
                await handle_voice_leave(member, before.channel)
            
            # Ignorar mudanças entre canais (não contar como saída/entrada)
            
        except Exception as e:
            print(f"Erro em on_voice_state_update: {e}")

async def handle_voice_join(member, channel):
    """Lida com entrada do usuário em canal de voz"""
    try:
        user_id_str = str(member.id)
        joined_at = time.time()
        
        # Iniciar sessão no banco
        success = database.start_voice_session(user_id_str, joined_at)
        
        if success:
            print(f"{member.display_name} entrou na call {channel.name}")
        else:
            print(f"{member.display_name} já estava em call (ignorado)")
            
    except Exception as e:
        print(f"Erro ao handle_voice_join: {e}")

async def handle_voice_leave(member, channel):
    """Lida com saída do usuário de canal de voz"""
    try:
        user_id_str = str(member.id)
        left_at = time.time()
        
        # Finalizar sessão e obter tempo
        session_duration = database.end_voice_session(user_id_str, left_at)
        
        if session_duration is not None:
            time_formatted = database.format_voice_time(session_duration)
            print(f"{member.display_name} saiu da call {channel.name} - Tempo: {time_formatted}")
        else:
            print(f"{member.display_name} saiu da call mas não tinha sessão ativa")
            
    except Exception as e:
        print(f"Erro ao handle_voice_leave: {e}")

# Função de registro para compatibilidade com estrutura atual
async def register(bot):
    """Registra o voice tracker no bot"""
    await setup(bot)
