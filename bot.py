import discord
from discord.ext import commands
from config import TOKEN
import asyncio


import events.ready as ready_event
import events.member_join as join_event
import events.message_handler as message_event
import events.bump as bump_event
import commands.misc as misc_commands
import commands.mush as mush_commands
import events.esporos as esporos_event

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

async def load_modules():
    print("Loading modules...")
    await ready_event.register(bot)
    print("ready_event loaded")
    await join_event.register(bot)
    print("join_event loaded")
    await message_event.register(bot)
    print("message_filter loaded")
    await misc_commands.register(bot)
    print("misc_commands loaded")
    await mush_commands.register(bot)
    print("mush_commands loaded")
    print("bump_event loaded")
    #await esporos_event.register(bot)
    print("All modules loaded!")
    print([command.name for command in bot.commands])
    
    # Sincronizar comandos uma única vez durante o setup
    try:
        from config import GUILD_ID
        if GUILD_ID:
            import discord
            guild_obj = discord.Object(id=int(GUILD_ID))
            
            # Sincronizar comandos diretamente para a guild
            synced = await bot.tree.sync(guild=guild_obj)
            print(f"Sincronizados {len(synced)} comandos no servidor {GUILD_ID}")
        else:
            synced = await bot.tree.sync()
            print(f"Sincronizados {len(synced)} comandos globais")
    except Exception as e:
        print("Erro ao sincronizar comandos:", e)

@bot.event
async def setup_hook():
    await load_modules()

if __name__ == "__main__":
    if not TOKEN:
        print("TOKEN não definido")
    else:
        bot.run(TOKEN)