import discord
from config import GUILD_ID
from views import ColorsView

async def register(bot):
    @bot.event
    async def on_ready():
        bot.add_view(ColorsView())
        print(f"Bot conectado como {bot.user}")

        try:
            if GUILD_ID:
                guild_obj = discord.Object(id=int(GUILD_ID))
                synced = await bot.tree.sync(guild=guild_obj)
                print(f"Sincronizados {len(synced)} comandos no servidor {GUILD_ID}")
            else:
                synced = await bot.tree.sync()
                print(f"Sincronizados {len(synced)} comandos globais")
        except Exception as e:
            print("Erro ao sincronizar comandos:", e)