import discord
import asyncio

async def register(bot):
    @bot.event
    async def on_ready():
        print(f"Bot conectado como {bot.user}")
        
        # Inicializar VoiceTracker
        print("🤖 Bot pronto, inicializando VoiceTracker...")
        from events.voice_tracker import get_voice_tracker
        voice_tracker = get_voice_tracker()
        if voice_tracker:
            await voice_tracker.initialize()
        else:
            print("❌ VoiceTracker não encontrado")
        
        # Iniciar o status automático após o bot estar pronto
        asyncio.create_task(update_status(bot))
        
        # Adicionar views persistentes
        from views import ColorsView, NormalColorsView, RarePingComponents, RarePingView, HelpView
        bot.add_view(ColorsView())
        bot.add_view(NormalColorsView())
        bot.add_view(RarePingComponents())
        bot.add_view(RarePingView())
        bot.add_view(HelpView())
        print("Views persistentes adicionadas")

async def update_status(bot):
    """Atualiza o status do bot periodicamente"""
    print("Iniciando função de status automático...")
    statuses = [
        "🍄 .gg/soull",
        "🍄 Protegendo o servidor",
        "🍄 .gg/soull",
        "🍄 Desenvolvido por 67xqw!",
        "🍄 Use /help para obter ajuda",
        "🍄 .gg/soull"
    ]
    
    while True:
        for status in statuses:
            try:
                print(f"Mudando status para: {status}")
                await bot.change_presence(activity=discord.Game(name=status))
                print(f"Status alterado com sucesso para: {status}")
                await asyncio.sleep(30)  # Muda status a cada 30 segundos
            except Exception as e:
                print(f"Erro ao atualizar status: {e}")
                await asyncio.sleep(5)